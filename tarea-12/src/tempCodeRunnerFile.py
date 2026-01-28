import json
import requests
import gradio as gr

# --- 1. CONFIGURACIÓN Y DATOS ---

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1"  # Recomendado usar llama3.1 para tools

# Base de datos (claves en minúscula para evitar errores de búsqueda)
ticket_prices = {
    "londres": "$799",
    "paris": "$899",
    "tokyo": "$1400",
    "berlin": "$499"
}

# --- 2. HERRAMIENTAS Y FUNCIONES ---

def get_ticket_price(destination_city):
    print(f"DEBUG: Buscando precio para {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Precio desconocido para esta ciudad")

# Definición de la herramienta (Schema para Ollama)
tool_definition = {
    "type": "function",
    "function": {
        "name": "get_ticket_price",
        "description": "Get the price of a return ticket to the destination city.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination_city": {
                    "type": "string",
                    "description": "The city that the customer wants to travel to",
                },
            },
            "required": ["destination_city"],
        },
    },
}

# --- 3. LÓGICA DE INTERACCIÓN CON OLLAMA ---

# --- 3. LÓGICA DE INTERACCIÓN CON OLLAMA ---

def chat_logic(history):
    # En Gradio con type="messages", history ya es una lista de dicts:
    # [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
    
    # Preparar mensajes para Ollama
    messages = []
    
    # 1. Contexto del sistema (siempre al principio)
    messages.append({
        "role": "system", 
        "content": "Eres un asistente de viajes útil. Usa la herramienta get_ticket_price cuando te pregunten por precios."
    })

    # 2. Añadir todo el historial (incluyendo el último mensaje del usuario que ya viene en 'history')
    messages.extend(history)

    # 1ª LLAMADA: Enviar mensaje + Definición de herramientas
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "tools": [tool_definition],
        "stream": False,
        "options": {"temperature": 0} 
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        message_response = response_data.get("message", {})
        tool_calls = message_response.get("tool_calls", [])

        # Si el modelo decide NO usar herramientas, devolver su respuesta textual
        if not tool_calls:
            return message_response.get("content", "No entendí la pregunta.")

        # SI HAY LLAMADA A HERRAMIENTA:
        # Agregamos la respuesta del asistente (la intención de llamar) al historial de this turn
        messages.append(message_response)

        # Procesar cada herramienta solicitada
        for tool in tool_calls:
            function_name = tool["function"]["name"]
            args = tool["function"]["arguments"]
            if isinstance(args, str):
                try: args = json.loads(args)
                except: args = {}
            
            if function_name == "get_ticket_price":
                city = args.get("destination_city")
                price_result = get_ticket_price(city)
                
                tool_msg = {
                    "role": "tool",
                    "content": json.dumps({"price": price_result}),
                    "name": function_name
                }
                if "id" in tool: tool_msg["tool_call_id"] = tool["id"]
                messages.append(tool_msg)

        # 2ª LLAMADA: Enviar el resultado de la herramienta a Ollama
        final_payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
        
        final_response = requests.post(OLLAMA_API_URL, json=final_payload)
        final_data = final_response.json()
        return final_data["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"

# --- 4. INTERFAZ GRADIO ---

def gradio_wrapper(message, history):
    # Añadir mensaje del usuario al historial
    history.append({"role": "user", "content": message})
    
    # Obtener respuesta del bot (pasamos todo el historial)
    bot_response = chat_logic(history)
    
    # Añadir respuesta del bot al historial
    history.append({"role": "assistant", "content": bot_response})
    
    # Devolver input vacío y el historial actualizado
    return "", history

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## ✈️ Asistente de Viajes FlightAI (Con Ollama)")
    
    # type="messages" eliminamos el argumento explícito ya que Gradio 6.0 lo asume/usa por defecto
    chatbot = gr.Chatbot(label="Chat", height=400)
    msg = gr.Textbox(
        show_label=False, 
        placeholder="Pregunta por precios (ej: Cuánto cuesta ir a Berlin?)..."
    )
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(gradio_wrapper, inputs=[msg, chatbot], outputs=[msg, chatbot])

if __name__ == "__main__":
    demo.launch()