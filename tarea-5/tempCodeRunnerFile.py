import sys
import requests
from bs4 import BeautifulSoup
import ollama
from ollama import Client
import textwrap
from datetime import datetime
from urllib.parse import urlparse


URLS_POR_DEFECTO = [
    "https://as.com/",
    "https://www.marca.com/",
    "https://www.mundodeportivo.com/",
    "https://www.sport.es/"
]
# Modelo de Ollama a utilizar
MODELO = "llama3.2" 
# Límite de caracteres para evitar sobrecargar el contexto del modelo
LIMITE_CHARS = 15000 
# Etiquetas HTML que se eliminarán para limpiar el texto  
ETIQUETAS_A_ELIMINAR = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'iframe', 'comment', 'noscript']



# Cliente de Ollama configurado al puerto por defecto (11434) [cite: 10]
OLLAMA_CLIENT = Client(host='http://localhost:11434')

def crear_prompts(titulo_pagina: str, texto_limpio: str) -> list:
    system_prompt = (
        "Eres un experto resumidor de noticias deportivas. "
        "Tu tarea es generar un resumen conciso y claro del texto provisto. "
        "El resumen debe estar siempre en ESPAÑOL y formateado con títulos en negrita "
        "y viñetas (formato Markdown). Ignora cualquier elemento de navegación, "
        "publicidad o texto irrelevante."
    )
    # User prompt: Incluye el título original de la página y el texto limpio [cite: 41]
    user_prompt = (
        f"Título de la fuente: '{titulo_pagina}'\n\n"
        f"Texto a resumir (máx. {LIMITE_CHARS} caracteres):\n\n"
        f"--- INICIO DEL TEXTO ---\n"
        f"{texto_limpio[:LIMITE_CHARS]}\n"
        f"--- FIN DEL TEXTO ---"
    )
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

# --- FUNCIONES DE SCRAPING Y LIMPIEZA ---

def obtener_html(url: str) -> str:
    """Descarga el HTML de la URL con manejo de errores de red/HTTP"""
    
    print(f"[INFO] Intentando descargar: {url}")
    # User-Agent para simular un navegador y evitar bloqueos 
    cabeceras = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # Tiempo de espera (timeout) razonable
        respuesta = requests.get(url, headers=cabeceras, timeout=10) 
        respuesta.raise_for_status() # Comprobamos si el codigo es 200
        return respuesta.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Fallo en la descarga de {url}: {e}")
        return ""

def limpiar_y_extraer_texto(html_content: str) -> tuple[str, str]:
    """Limpia el HTML y extrae el texto legible del cuerpo"""
    if not html_content:
        return "", ""

    # Usamos 'html.parser' para parsear el HTML
    sopa = BeautifulSoup(html_content, 'html.parser')
    
    # Intenta obtener el título de la página para el prompt
    titulo = sopa.title.string.strip()
    
    # Eliminar etiquetas irrelevantes (navegación, scripts, etc.)
    for etiqueta in ETIQUETAS_A_ELIMINAR:
        for elemento in sopa.find_all(etiqueta):
            elemento.decompose()
            
    # Intentar obtener el contenido principal (cuerpo de la página)
    cuerpo = sopa.find('body')
    if not cuerpo:
        print("[ERROR] No se encontró la etiqueta <body>. Extrayendo de <html>.")
        cuerpo = sopa.find('html')

    if not cuerpo:
        print("[ERROR] No hay texto útil en el HTML (o estructura no estándar)[cite: 57].")
        return titulo, ""

    # Extraer todo el texto legible y limpiar espacios/saltos de línea excesivos
    texto_limpio = cuerpo.get_text(separator=' ', strip=True)
    
    return titulo, texto_limpio

# --- FUNCIÓN DE OLLAMA ---

def obtener_resumen_ollama(mensajes: list) -> str:
    """Llama al modelo de Ollama para obtener el resumen"""
    try:
        print(f"[INFO] Enviando {len(mensajes[1]['content'])} chars a Ollama con modelo '{MODELO}'...")
        # Recibimos la salida completa (no streaming) para asegurar el formato y simplificar (Justificar en README) [cite: 44]
        respuesta = OLLAMA_CLIENT.chat(
            model=MODELO,
            messages=mensajes,
            stream=False 
        )
        # Extraer solo el contenido textual del resumen
        return respuesta['message']['content']
    except Exception as e:
        # Manejo de error: Modelo no disponible o servidor Ollama apagado
        print(f"[ERROR] Fallo en la llamada a Ollama: {e}")
        print("  -> Asegúrate que Ollama esté corriendo y que el modelo '{MODELO}' esté descargado.")
        return ""

# --- FUNCIONES DE SALIDA Y FORMATO ---

def imprimir_resumen(url: str, tamano_texto: int, nombre_medio: str, resumen_texto: str):
    """Muestra el resultado por consola con formato claro (títulos y viñetas)"""
    
    # Encabezado informativo 
    print("\n" + "="*80)
    print(f"[INFO] Resumiendo: {url} ({tamano_texto} chars)")
    print("="*80)
    
    # Título de resumen 
    print(f"RESUMEN: {nombre_medio} - {url}")
    print("="*80)
    
    # Cuerpo del resumen (el modelo ya genera el markdown)
    print(resumen_texto)
    
    # Separador de cierre 
    print("="*80 + "\n")


def guardar_resumen(url: str, resumen_texto: str):
    """(Opcional) Guarda el resumen a archivo.md con marca temporal"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"salidas/{urlparse(url).netloc}_{timestamp}.md".replace('www.','')
    
    try:
        # Asegura que la carpeta salidas/ exista
        import os
        os.makedirs('salidas', exist_ok=True)
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"# Resumen de {url}\n\n")
            f.write(resumen_texto)
        print(f"[INFO] Resumen guardado en: {nombre_archivo}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo: {e}")

# --- FUNCIÓN PRINCIPAL ---

def procesar_url(url: str):
    """Función que orquesta todo el proceso para una URL."""
    nombre_medio = urlparse(url).netloc # Extrae el dominio como nombre del medio

    # 1. Descarga y limpieza de HTML
    html_content = obtener_html(url)
    if not html_content:
        return
        
    titulo_pagina, texto_limpio = limpiar_y_extraer_texto(html_content)
    
    tamano_texto = len(texto_limpio)
    if tamano_texto == 0:
        print(f"[ERROR] La URL {url} no contiene texto útil después de la limpieza. Saltando.")
        return
    
    # 2. Diseño de prompts
    mensajes = crear_prompts(titulo_pagina, texto_limpio)
    
    # 3. Llamada al modelo de Ollama
    resumen = obtener_resumen_ollama(mensajes)
    
    if not resumen:
        return
        
    # 4. Impresión en consola
    imprimir_resumen(url, tamano_texto, nombre_medio, resumen)
    
    # 5. Guardar opcionalmente
    guardar_resumen(url, resumen)


def main():
    """Punto de entrada del programa. Gestiona las URLs de entrada"""
    # Si se reciben argumentos, procesa esas URLs 
    if len(sys.argv) > 1:
        urls_a_procesar = sys.argv[1:]
    # Si no se reciben argumentos, usa las URLs por defecto
    else:
        urls_a_procesar = URLS_POR_DEFECTO

    print(f"--- Iniciando resumen deportivo con Ollama ({MODELO}) ---")
    for url in urls_a_procesar:
        procesar_url(url)
    print("--- Proceso finalizado ---")

if __name__ == "__main__":
    main()