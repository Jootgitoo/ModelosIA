import json
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


def handle_tool_call(message):

    # 1. Obtener qué pide la IA
    tool_call = message.tool_calls[0]

    # 2. Decodificar los argumentos (ej: {"destination_city": "Berlin"})
    arguments = json.loads(tool_call.function.arguments)
    city = arguments.get('destination_city')

    # 3. Ejecutar nuestra función Python (Paso 1)
    price = get_ticket_price(city)

    # 4. Preparar la respuesta para la IA
    response = {
        "role": "tool",
        "content": json.dumps({"destination_city": city, "price": price}),
        "tool_call_id": tool_call.id
    }
    return response, city



with gr.Blocks(theme=gr.themes.Soft()):
    gr.Markdown("## ✈️ Asistente de Viajes IA")
    
    # A. Primer recuadro: Las conversaciones
    chatbot = gr.Chatbot(label="Historial del Chat", height=400)
    
    # B. Textbox para el usuario
    msg = gr.Textbox(
        show_label=False, 
        placeholder="Escribe una ciudad aquí (ej: London) y presiona Enter o Enviar..."
    )
    
    # C. Botón de enviar
    btn = gr.Button("Enviar 📤")
    
    # 3. Manejo de Eventos (Hacer que funcione)
    # Al hacer clic en el botón
    btn.click(handle_tool_call, inputs=[msg, chatbot], outputs=[msg, chatbot])

    # Al presionar Enter en la caja de texto
    msg.submit(handle_tool_call, inputs=[msg, chatbot], outputs=[msg, chatbot])