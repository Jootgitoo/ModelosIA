# prueba_a.py — Prueba de conexión con Ollama usando la API HTTP

# 1) Imports necesarios
import requests  # Para hacer la petición HTTP
import json 

# 2) Constantes
OLLAMA_API = "http://localhost:11434/api/chat"
ENCABEZADOS = {"Content-Type": "application/json"}
MODELO = "llama3.2"

# 3) Mensaje del usuario
mensaje = [
    {"role": "user", "content": "Describe some of the business applications of Generative AI"}
]

# 4) Construcción del datos_mensaje
datos_mensaje = {
    "MODELO": MODELO,
    "mensaje": mensaje,
    "stream": True  
    # False --> quiero toda la respuesta de golpe (más fácil de manejar)
    # True --> el servidor enviaría tokens poco a poco en tiempo real
}

# 5) Envío de la petición y manejo de errores
def main():
    try:
        # Envío la petición POST a la API de Ollama
        resp = requests.post(OLLAMA_API, json=datos_mensaje, headers=ENCABEZADOS, timeout=120)

        # Verifico que tengamos código 200
        resp.raise_for_status()

        # Parseo la respuesta JSON
        data = resp.json()

        # Imprimo la respuesta
        print(data["message"]["content"])

    except requests.exceptions.ConnectionError as e:
        print("[ERROR] El servidor Ollama no está disponible. Verifica que esté corriendo con 'ollama serve'.")
        print(e)

    except KeyError as e:
        print("[ERROR] El MODELOo probablemente no está descargado o la respuesta no tiene el formato esperado.")
        print("Verifica con:  ollama pull llama3.2")
        print(e)

    except Exception as e:
        print("[ERROR] Ocurrió un error inesperado.")
        print(e)


if __name__ == "__main__":
    main()
