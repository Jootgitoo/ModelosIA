# La open_api_key y anthropic_api_key no funcionan al no tener quotas gratuitas

import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai


#Cargamos el fichero .env
load_dotenv()


#Asignar claves a veriables desde el entorno
open_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")


# Verificar que las claves se han cargado correctamente
if open_api_key:
    print("Clave OpenAi cargada: {open_api_key[:8]}...")
else:
    print("Error: Clave OpenAi no encontrada.")
    
if anthropic_api_key:
    print("Clave Anthropic cargada: {anthropic_api_key[:8]}...")
else:
    print("Error: Clave Anthropic no encontrada.")
    
if google_api_key:
    print("Clave Google cargada: {google_api_key[:8]}...")
else:
    print("Error: Clave Google no encontrada.")
    

# Promt del Sistema (Contexto)
system_message = "Eres un asistenteque que cuentas chistes muy graciosos."

#Promt de Usuario (Petición)
user_promt = "Cuenta un chiste divertido a una audencia de científicos de datos"

# Eestructura de Datos (Patrón de Mensajes)
promts = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_promt}
]


# -------------- LLAMADA A OPENAI -----------------------------------

# Protocolo de Llamada a la API de OpenAI
openai = OpenAI()

# Realizamos la llamada
completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=promts,
    temperature=0.2,
    max_tokens=50
)

# Extraemos y mostramos la respuesta
respuesta = completion.choices[0].message.content
print("Respuesta de OpenAI: {respuesta}")
   
    
# ---------------------- LLAMADA A ANTHROPIC -------------------------------

# Conectamos con el cliente de Anthropic
claude = anthropic.Anthropic()

# Realizamos la llamada
message = claude.messages.create(
    model="claude-3.5-sonnet-20240620",
    max_tokens=50,
    #max_tokens=200, Lo dejo puesto para que no tenga limite de tokens
    temperature=0.6,
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_promt}
    ]
)

# Extraemos y mostramos la respuesta
respuesta = message.content[0].text()
print("Respuesta de Anthropic: {respuesta}")


# -------------------- LLAMADA A LA API DE GOOGLE -------------------------------

# Protocolo de Llamada a la API de Google
google.generativeai.configure(api_key=google_api_key)
gemini = google.generativeai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction=system_message
)

# Definimos la temperatura del modelo
configuracion = google.generativeai.types.GenerationConfig(
    temperature=0.9,
    max_output_tokens=100
)

# Realizamos la llamada
response = gemini.generate_content(
    user_promt,
    generation_config=configuracion
)

print(response.text)

# -------------------- LLAMADA A OLLAMA (Local) -------------------------------
import requests

# URL por defecto de la API de Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate" 
OLLAMA_MODEL = "llama3" # Asegúrate de que este modelo esté descargado

# Combinamos los prompts para el formato de Ollama/llama
full_prompt = f"Eres un asistente que cuentas chistes muy graciosos. Cuenta un chiste divertido a una audencia de científicos de datos"

# Configuramos la petición para limitar la longitud
payload = {
    "model": OLLAMA_MODEL,
    "prompt": full_prompt,
    "stream": False,
    "options": {
        # El parámetro para limitar tokens de salida en Ollama es num_predict
        "num_predict": 100, 
        "temperature": 0.9
    }
}

try:
    # Realizamos la llamada HTTP
    response = requests.post(OLLAMA_API_URL, json=payload)
    response.raise_for_status() # Manejo básico de errores HTTP
    
    # Extraemos y mostramos la respuesta
    data = response.json()
    respuesta = data.get("response", "Error al procesar la respuesta.")
    print(f"Respuesta de Ollama: {respuesta}")

except requests.exceptions.RequestException as e:
    print(f"Error al conectar con Ollama: {e}")