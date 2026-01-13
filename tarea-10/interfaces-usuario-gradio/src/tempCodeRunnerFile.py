import gradio as gr
#from dotenv import load_dotenv
import os

def shout(text):
    return text.upper()


gr.Interface(fn=shout, input="text", output="text").launch()