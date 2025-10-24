# prueba_b.py — Conexión a Ollama usando el SDK oficial
# Autor: Carlos

import ollama  # SDK de Ollama, más directo que usar requests

MODEL = "llama3.2"
messages = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

try:
    # Llamamos directamente al modelo usando el método 'chat' del SDK
    response = ollama.chat(model=MODEL, messages=messages)

    # Mostramos el texto generado por el modelo
    print(response["message"]["content"])

except ollama.ResponseError as e:
    print("[ERROR] El modelo no está disponible o hubo un fallo al generar la respuesta.")
    print(e)

except Exception as e:
    print("[ERROR] Ocurrió un error inesperado. Verifica que Ollama esté en ejecución.")
    print(e)
