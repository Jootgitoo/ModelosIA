import json
import requests
import gradio as gr

# Base de datos inventada
ticket_prices = {
    "londres": "$799",
    "paris": "$899",
    "tokyo": "$1400",
    "berlin": "$499"
}


def get_ticket_price(destination_city):
    '''
    Busca el precio del billete en el diccionario
    '''
    print(f"DEBUG: Buscando precio para {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Precio desconocido para esta ciudad")


# Definición de la herramienta
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


def chat_logic(history):
    '''
    Llamada a Ollama con la herramienta del diccionario
    '''

    OLLAMA_API_URL = "http://localhost:11434/api/chat"

    #Modelo 3.1 por que es el que puede acceder a herramientas
    OLLAMA_MODEL = "llama3.1"

    #Preparación de mensajes
    messages = []
    
    #Prompt del Sistema: Define el comportamiento y las herramientas disponibles
    messages.append({
        "role": "system", 
        "content": "Eres un asistente de viajes útil. Usa la herramienta get_ticket_price cuando te pregunten por precios."
    })

    #Guardamos el historial de la conversación
    messages.extend(history)

    # PRIMERA LLAMADA A OLLAMA (Detectar Intención)
    # Enviamos el historial junto con la definición de herramientas disponibles
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "tools": [tool_definition], # Le decimos a Ollama qué funciones puede usar
        "stream": False,
        "options": {"temperature": 0}
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        message_response = response_data.get("message", {})
        tool_calls = message_response.get("tool_calls", [])

        #Si el modelo responde sin usar herramientas
        if not tool_calls:
            return message_response.get("content", "No entendí la pregunta.")

        #Si el modelo decide usar una herramienta
        # Primero, añadimos la respuesta "intención" del asistente al historial
        messages.append(message_response)

        #EJECUCIÓN DE HERRAMIENTAS
        for tool in tool_calls:
            function_name = tool["function"]["name"]
            
            #Limpieza y parseo de argumentos
            args = tool["function"]["arguments"]
            if isinstance(args, str):
                try: args = json.loads(args)
                except: args = {}
            
            #Verificamos qué función se solicitó
            if function_name == "get_ticket_price":
                city = args.get("destination_city")
                #Ejecutamos nuestra función Python local
                price_result = get_ticket_price(city)
                
                #Preparamos el mensaje de resultado para el modelo
                tool_msg = {
                    "role": "tool",
                    "content": json.dumps({"price": price_result}),
                    "name": function_name
                }
                #Id de llamada (requerido por estándares modernos)
                if "id" in tool: tool_msg["tool_call_id"] = tool["id"]
                
                messages.append(tool_msg)

        #SEGUNDA LLAMADA A OLLAMA (Respuesta Final)
        # Enviamos el historial actualizado (incluyendo el resultado de la herramienta)
        # para que el modelo genere una respuesta natural al usuario
        final_payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
        
        final_response = requests.post(OLLAMA_API_URL, json=final_payload)
        final_data = final_response.json()
        
        #Devolvemos el texto final generado
        return final_data["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"



def gradio_wrapper(message, history):
    #Añadir mensaje del usuario al historial
    history.append({"role": "user", "content": message})
    
    #Obtener respuesta del bot (pasamos todo el historial)
    bot_response = chat_logic(history)
    
    #Añadir respuesta del bot al historial
    history.append({"role": "assistant", "content": bot_response})
    
    #Devolver input vacío y el historial actualizado
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