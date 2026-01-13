import gradio as gr
#from dotenv import load_dotenv
import os

def shout(text):
    return text.upper()

view = gr.Interface(
    fn=shout,
    inputs=[gr.Textbox(label="Tu mensaje:", lines=6)],
    outputs=[gr.Textbox(label="Respuesta:", lines=8)],
    flagging_mode="never"
)view.launch()

#Paso 3