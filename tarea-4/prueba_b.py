# prueba_b.py — Conexión a Ollama usando el SDK oficial

import ollama 

MODELO = "llama3.2"
mensaje = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

try:
    # Llamamos directamente al MODELOo usando el método 'chat' del SDK
    response = ollama.chat(MODELO=MODELO, mensaje=mensaje)

    # Mostramos el texto generado por el MODELOo
    print(response["message"]["content"])

except ollama.ResponseError as e:
    print("[ERROR] El MODELO no está disponible o hubo un fallo al generar la respuesta.")
    print(e)

except Exception as e:
    print("[ERROR] Ocurrió un error inesperado. Verifica que Ollama esté en ejecución.")
    print(e)
