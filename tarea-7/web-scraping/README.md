# 🚀 Generador de Folletos Corporativos con IA

Aplicación que genera folletos corporativos profesionales mediante web scraping y LLM local (Ollama).

## 📋 Características

- ✅ Web scraping responsable con respeto a `robots.txt`
- ✅ Selección inteligente de enlaces con LLM
- ✅ Generación de folletos en Markdown
- ✅ Exportación a HTML y PDF (opcional)
- ✅ Dos tonos: formal y humorístico
- ✅ Modo mock para probar sin LLM
- ✅ Rate limiting y manejo de errores robusto

## 🛠️ Requisitos

### Sistema
- Python 3.8+
- Ollama instalado y ejecutándose ([Instalar Ollama](https://ollama.ai))

### Modelo de Ollama
```bash
# Descargar el modelo llama3
ollama pull llama3

# Verificar que está instalado
ollama list
```

## 📦 Instalación

### 1. Clonar o crear el proyecto

```bash
mkdir brochure-ai
cd brochure-ai
```

### 2. Crear estructura de directorios

```bash
mkdir -p src outputs prompts tests
touch src/__init__.py
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si es necesario
```

El archivo `.env` por defecto ya está configurado para Ollama local:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
USER_AGENT=CorporateBrochureBot/1.0 (Educational Project)
REQUEST_TIMEOUT=10
RATE_LIMIT_DELAY=1.0
MOCK_MODE=false
```

## 🚀 Uso

### Uso básico

```bash
python -m src.cli --company "HuggingFace" --url "https://huggingface.co"
```

### Con todas las opciones

```bash
python -m src.cli \
  --company "Anthropic" \
  --url "https://www.anthropic.com" \
  --tone formal \
  --export-html \
  --export-pdf \
  --output outputs \
  --log-level INFO
```

### Modo mock (sin Ollama)

```bash
python -m src.cli --company "Test Company" --url "https://example.com" --mock
```

## 📊 Estructura del Proyecto

```
brochure-ai/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── scraping.py          # Web scraping con BeautifulSoup
│   ├── llm_client.py        # Cliente de Ollama
│   ├── link_selector.py     # Selección de enlaces con LLM
│   ├── compiler.py          # Compilación de contenidos
│   ├── brochure.py          # Generación del folleto
│   ├── cli.py               # Interfaz de línea de comandos
│   └── utils.py             # Utilidades
├── prompts/                 # (opcional) prompts en archivos
├── outputs/                 # Folletos generados
├── tests/                   # Tests
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de configuración
├── .env                    # Tu configuración (no subir a git)
└── README.md               # Este archivo
```

## 🎯 Flujo de Funcionamiento

1. **Scraping**: Descarga la página principal y extrae todos los enlaces
2. **Filtrado**: Pre-filtra enlaces obviamente irrelevantes
3. **Selección LLM**: Usa Ollama para seleccionar 3-8 enlaces más relevantes
4. **Compilación**: Descarga y limpia el contenido de cada página seleccionada
5. **Generación**: Usa Ollama para generar el folleto en Markdown
6. **Exportación**: Guarda MD, HTML y/o PDF

## 🧪 Casos de Prueba

### 1. Empresa tech estándar
```bash
python -m src.cli --company "HuggingFace" --url "https://huggingface.co"
```

### 2. Empresa con muchos enlaces relativos
```bash
python -m src.cli --company "Mozilla" --url "https://www.mozilla.org"
```

### 3. Empresa minimalista
```bash
python -m src.cli --company "Basecamp" --url "https://basecamp.com"
```

## ⚙️ Decisiones de Diseño

### Arquitectura Modular
- Cada componente (scraping, LLM, compilación) es independiente
- Facilita testing y mantenimiento
- Permite cambiar Ollama por otra API fácilmente

### Web Scraping Responsable
- Respeta `robots.txt` cuando sea posible
- Rate limiting configurable (1 seg por defecto)
- User-Agent identificable
- Timeout en peticiones
- Manejo robusto de errores HTTP

### Manejo de LLM
- Reintentos automáticos en caso de error
- Extracción de JSON incluso si viene con texto adicional
- Reparación básica de JSON malformado
- Temperatura ajustable según el tipo de respuesta

### Límites de Contenido
- Máximo 5000 caracteres por página compilada
- Límite de 20 enlaces enviados al LLM
- Pre-filtrado de enlaces irrelevantes

## 🔒 Consideraciones Éticas

### Respeto al Scraping
- ✅ Verificamos `robots.txt` antes de scrapear
- ✅ Usamos rate limiting (min. 1 segundo entre requests)
- ✅ User-Agent identificable que indica propósito educativo
- ✅ No recolectamos datos personales
- ✅ Solo páginas públicas

### Disclaimer
Todos los folletos generados incluyen un disclaimer indicando:
- Contenido generado automáticamente
- Fecha de generación
- Necesidad de verificación antes de uso externo
- Carácter no oficial del documento

### Privacidad
- No almacenamos contenido descargado por defecto
- No enviamos datos a terceros (todo local con Ollama)
- No recolectamos información de usuarios

## 🐛 Limitaciones Conocidas

1. **Dependencia de estructura HTML**: Sitios muy dinámicos (JavaScript) pueden no scraparse bien
2. **Calidad del LLM**: Depende del modelo de Ollama usado (llama3 recomendado)
3. **Idioma**: Optimizado para inglés, puede funcionar en español pero con menor calidad
4. **PDF**: Requiere dependencias del sistema (cairo, pango) que pueden ser complicadas en Windows
5. **Rate limiting básico**: No detecta headers `Retry-After`

## 🔧 Troubleshooting

### Ollama no responde
```bash
# Verificar que Ollama está corriendo
ollama list

# Iniciar Ollama si está cerrado
ollama serve
```

### Error al importar ollama
```bash
pip install ollama
```

### Error de JSON del LLM
- El sistema intenta reparar JSON automáticamente
- Si falla repetidamente, intenta con `--mock` para verificar el resto del pipeline

### PDF no se genera
- Instalar dependencias del sistema:
```bash
# Ubuntu/Debian
sudo apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0

# macOS
brew install cairo pango gdk-pixbuf libffi
```

## 📝 Tests

```bash
# Instalar pytest
pip install pytest

# Ejecutar tests (cuando los crees)
pytest tests/
```

## 🎨 Ejemplos de Salida

Los folletos generados incluyen:

- 📌 Título y tagline
- 📄 Descripción de la empresa (1-2 párrafos)
- 🛠️ Productos/Servicios (bullets)
- 🎯 Clientes objetivo
- ⭐ Casos de éxito (si disponible)
- 💡 Cultura y valores
- 💼 Carreras y beneficios (si disponible)
- 📞 Call to Action
- ⚖️ Disclaimer ético

## 🚀 Mejoras Futuras

- [ ] UI con Streamlit o Gradio
- [ ] Detección automática de idioma
- [ ] Caché de páginas descargadas
- [ ] Tests de integración
- [ ] Soporte multilingüe
- [ ] Métricas de tiempo y tokens
- [ ] Selector de perfil (cliente/inversor/candidato)

## 📄 Licencia

Proyecto educativo - Uso libre para aprendizaje

## 👤 Autor

Tu Nombre - Práctica de IA y Web Scraping

---

**Nota**: Este proyecto fue creado con fines educativos. Respeta siempre los términos de servicio de los sitios web que scrapees.