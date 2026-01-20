import dotenv
import os
import gradio as gr


#Cargamos el fichero .env
load_dotenv()


#Asignar claves a veriables desde el entorno
open_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")


# Promt del Sistema (Contexto)
system_message = "Eres un asistenteque que cuentas chistes muy graciosos."

#Promt de Usuario (Petición)
user_promt = "Cuenta un chiste divertido a un grupo de programadores"

# Eestructura de Datos (Patrón de Mensajes)
promts = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_promt}
]


# -------------- LLAMADA A OPENAI -----------------------------------

def consultar_gpt():
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
   

# -------------------- LLAMADA A LA API DE GOOGLE (Gemini)-------------------------------

def consultar_gemini():
    # Protocolo de Llamada a la API de Google
    google.generativeai.configure(api_key=google_api_key)
    gemini = google.generativeai.GenerativeModel(
        model_name="gemini-1.5-flash",
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



# ---------------------- LLAMADA A ANTHROPIC (Claude)-------------------------------

def consultar_claude():
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


def generar_respuesta(prompt, modelo_seleccionado):
    # Esta función debe recibir la elección del usuario desde la interfaz gráfica.
    # Debe usar una estructura condicional (if/elif/else) para llamar a la función específica según el modelo elegido.
    # Manejo de errores: Si el usuario no escribe nada o selecciona un modelo no válido, la función debe devolver un mensaje de error amigable.


#Paso 4: Diseño de la Interfaz (GUI)
# Utilizando la librería Gradio, construye una interfaz que cumpla con los siguientes requisitos visuales:
# 1.
# Entrada: Un cuadro de texto (Textbox) de varias líneas para la pregunta.
# 2.
# Selector: Un menú desplegable (Dropdown) que liste claramente las opciones: "ChatGPT", "Gemini" y "Claude". Por defecto debe haber uno seleccionado.
# 3.
# Salida: Un área de respuesta que interprete formato Markdown. Esto es vital para que si la IA genera código o tablas, se vean correctamente (negritas, bloques de código, etc.).
# 4.
# Botones: Un botón de "Enviar" y otro de "Limpiar".

def procesar_pregunta(pregunta, modelo):
    if not pregunta.strip():
        return "⚠️ **Introduce una pregunta antes de enviar.**"
    
    return f"""
    ### Modelo seleccionado
    **{modelo}**

    ### Pregunta
    {pregunta}

    *(Aquí iría la respuesta generada por la IA)*
    """

with gr.Blocks(title="Comparador de IAs") as demo:
    
    gr.Markdown("## 🤖 Comparador de Modelos de IA")
    
    # 1. Entrada: Textbox multilínea
    pregunta = gr.Textbox(
        label="Pregunta",
        placeholder="Escribe aquí tu pregunta...",
        lines=5
    )
    
    # 2. Selector: Dropdown
    modelo = gr.Dropdown(
        choices=["ChatGPT", "Gemini", "Claude"],
        value="ChatGPT",   # seleccionado por defecto
        label="Modelo de IA"
    )
    
    # 3. Salida: Markdown
    salida = gr.Markdown(label="Respuesta")
    
    # 4. Botones
    with gr.Row():
        btn_enviar = gr.Button("Enviar")
        btn_limpiar = gr.Button("Limpiar")
    
    btn_enviar.click(
        fn=procesar_pregunta,
        inputs=[pregunta, modelo],
        outputs=salida
    )
    
    btn_limpiar.click(
        fn=lambda: ("", "", ""),
        outputs=[pregunta, modelo, salida]
    )

demo.launch()
