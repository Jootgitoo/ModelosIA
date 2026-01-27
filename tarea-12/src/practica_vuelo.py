import json
import requests
import gradio as gr

# 1. Base de datos ficticia de precios
ticket_prices = {
    "london": "$799",
    "paris": "$899",
    "tokyo": "$1400",
    "berlin": "$499"
}


# 2. Función Python real para obtener el precio
def get_ticket_price(destination_city):
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown") #Unknow es lo que devuelve si no encuentra la ciudad


# 3. Definición de la herramienta para OpenAI
price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city. Call this whenever you need to know the ticket price.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

# Lista de herramientas habilitadas
tools = [{"type": "function", "function": price_function}]



# 4. Manejador de llamadas a herramientas
def handle_tool_call(message):
    """
    Ejecuta la herramienta solicitada por el modelo.
    Se espera que 'message' sea un diccionario con la estructura de respuesta de Ollama.
    """
    try:
        tool_call = message.get("tool_calls", [])[0]
        function_name = tool_call["function"]["name"]
        
        # Validar que sea la función correcta
        if function_name == "get_ticket_price":
            # Argumentos ya vienen como diccionario en la respuesta de Ollama (generalmente)
            # Pero a veces vienen como string en 'arguments', depende de la versión.
            # La API de chat de Ollama suele devolver un dict en 'arguments' si es JSON mode o tool mode bien hecho.
            args = tool_call["function"]["arguments"]
            
            # Si es un string (algunos modelos/versiones), lo parseamos
            if isinstance(args, str):
                arguments = json.loads(args)
            else:
                arguments = args
                
            city = arguments.get('destination_city')
            
            print(f"Tool get_ticket_price called for {city}") # Log requerido
            
            # Ejecutar función real
            price = get_ticket_price(city)
            
            # Respuesta formateada para el historial del chat
            return {
                "role": "tool",
                "content": json.dumps({"destination_city": city, "price": price}),
                # Ollama a veces no usa tool_call_id strictamente como OpenAI, pero lo mantenemos si existe
                # Para Ollama simple, basta con enviar el rol tool.
            }
    except Exception as e:
        print(f"Error handling tool call: {e}")
        return {"role": "tool", "content": "Error executing tool"}

# -------------------- LÓGICA DEL CHAT CON OLLAMA -------------------------------

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1" # Usando llama3.1 que soporta tools mejor, o llama3

def chat_logic(user_message, history):
    """
    Lógica principal del chat:
    1. Envia mensaje de usuario a Ollama.
    2. Si Ollama pide herramienta -> Ejecutar y devolver resultado -> Segunda llamada a Ollama.
    3. Devolver respuesta final.
    """
    
    # Construir historial de mensajes
    # System prompt
    messages = [{
        "role": "system", 
        "content": "I am a helpful assistant for an Airline called FlightAI."
    }]
    
    # Añadir historial previo (convertir formato Gradio a formato API)
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
        
    # Añadir mensaje actual
    messages.append({"role": "user", "content": user_message})
    
    # Primera llamada a Ollama
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "tools": tools # Definido arriba
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        message = response_data.get("message", {})
        
        # Verificar si quiere usar herramientas
        if message.get("tool_calls"):
            # A. El modelo quiere usar una herramienta
            
            # 1. Añadir el mensaje de intención del asistente al historial
            messages.append(message)
            
            # 2. Ejecutar la herramienta
            tool_response = handle_tool_call(message)
            
            # 3. Añadir el resultado de la herramienta al historial
            messages.append(tool_response)
            
            # 4. Segunda llamada a Ollama con el resultado
            payload_2 = {
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "tools": tools
            }
            
            response_2 = requests.post(OLLAMA_API_URL, json=payload_2)
            response_2.raise_for_status()
            final_response = response_2.json()["message"]["content"]
            
        else:
            # B. Respuesta directa (conversación normal)
            final_response = message.get("content", "")
            
        return final_response
            
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


# -------------------- INTERFAZ GRADIO -------------------------------

def gradio_wrapper(message, history):
    # Wrapper simple porque chat_logic devuelve solo el string de respuesta
    # Gradio ChatInterface maneja el append al historial automaticamente si usamos la forma simple
    # Pero aqui estamos usando Blocks con Chatbot manual en el codigo original.
    # El usuario tenia: handle_tool_call(msg, chatbot) -> output [msg, chatbot]
    
    # Ajustamos para el estilo 'manual' del codigo original pero aprovechando la logica nueva
    
    # 'history' en el componente Chatbot de Gradio es una lista de listas [[user, bot], ...]
    bot_response = chat_logic(message, history)
    
    history.append((message, bot_response))
    return "", history # Limpiar msg input, devolver nuevo history


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## ✈️ Asistente de Viajes FlightAI")
    
    chatbot = gr.Chatbot(label="Chat History", height=400)
    msg = gr.Textbox(
        show_label=False, 
        placeholder="Ask regarding ticket prices (e.g. London)..."
    )
    btn = gr.Button("Send 📤")
    
    # Eventos
    btn.click(gradio_wrapper, inputs=[msg, chatbot], outputs=[msg, chatbot])
    msg.submit(gradio_wrapper, inputs=[msg, chatbot], outputs=[msg, chatbot])

if __name__ == "__main__":
    demo.launch()
