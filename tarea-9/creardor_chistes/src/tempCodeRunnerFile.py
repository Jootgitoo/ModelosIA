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
        "num_predict": 50, 
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