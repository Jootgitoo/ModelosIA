import gradio as gr
import requests

def call_ollama(text):
    OLLAMA_API_URL = "http://localhost:11434/api/generate" 
    OLLAMA_MODEL = "llama3"

    # 1. Definimos la PERSONALIDAD (System Prompt)
    system_instruction = "Eres un generador de excusas creativo. Responde ÚNICAMENTE con la excusa exacta, sin introducciones, sin saludos y sin ofrecer más ayuda."

    # 2. Combinamos la personalidad con el TEXTO DEL USUARIO
    # Aquí es donde estaba el fallo: ahora concatenamos la instrucción + el input del usuario
    final_prompt = f"{system_instruction}\n\nLa situación es: {text}\nExcusa:"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": final_prompt,  # Enviamos el prompt combinado
        "stream": False,
        "options": {
            "num_predict": 100, 
            "temperature": 0.7 # Subí un poco la temperatura para que sea más creativa
        }
    }
    
    # 3. Hacemos la petición (añadí esta parte por si te faltaba)
    response = requests.post(OLLAMA_API_URL, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return f"Error: {response.status_code}"

view = gr.Interface(
    fn=call_ollama,
    inputs=[gr.Textbox(label="Tu mensaje:", lines=6)],
    outputs=[gr.Textbox(label="Respuesta:", lines=8)],
    flagging_mode="never"
)
view.launch()

