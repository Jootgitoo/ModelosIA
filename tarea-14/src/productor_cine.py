import torch
import os
import asyncio # Necesario para el audio
from pypdf import PdfReader
from deep_translator import GoogleTranslator
import edge_tts
from diffusers import StableDiffusionPipeline
from transformers import pipeline
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# Configuración del Hardware
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

print(f"🎬 Iniciando estudio en: {device}")

def leer_pdf_y_dividir(ruta_pdf):
    reader = PdfReader(ruta_pdf)
    texto_completo = ""
    for page in reader.pages:
        texto_completo += page.extract_text()
    
    # CAmbiamos los salto de línea por espacios
    texto_limpio = texto_completo.replace('\n', ' ')
    
    # Dividimos por frases
    frases = [f.strip() + "." for f in texto_limpio.split('.') if len(f) > 10]
    
    # Agrupamos frases en "escenas" (ej. cada 2 frases es una escena)
    escenas = []
    chunk_size = 2 
    for i in range(0, len(frases), chunk_size):
        bloque = " ".join(frases[i:i+chunk_size])
        if bloque:
            escenas.append(bloque)
            
    return escenas[:4] # Limitamos a 4 escenas para el tráiler

# Cargar el modelo de lenguaje (LLM)
pipe_llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch_dtype, device=device)

def generar_prompt_base(texto_escena):
    # Estructura específica de TinyLlama
    prompt = f"<|user|>\nDescribe the visual action in this scene for a movie shot in 15 words:\n{texto_escena}\n<|assistant|>"
    outputs = pipe_llm(prompt, max_new_tokens=60, do_sample=True, temperature=0.7)
    return outputs[0]['generated_text'].split("<|assistant|>")[-1].strip()


def inyectar_vestuario(texto_original, prompt_base):
    texto_lower = texto_original.lower()
    prompt_mejorado = prompt_base
    
    # --- LÓGICA ACERO PURO (REAL STEEL) ---
    if 'atom' in texto_lower:
        prompt_mejorado += ", (rusted grey fighting robot:1.5), glowing blue eyes, mechanical face, boxing stance, battle damage"
    elif 'zeus' in texto_lower:
        prompt_mejorado += ", (massive shiny black robot:1.5), green neon lights, futuristic armor, menacing look"
    elif 'charlie' in texto_lower:
        prompt_mejorado += ", (man with short beard and leather jacket:1.2), looking at robot"
    else:
        # Si no menciona a nadie, aseguramos estética robot
        prompt_mejorado += ", robots boxing in a dirty arena, metal textures"

    # Estrategia Close-Up para evitar caras deformes [cite: 156]
    prompt_mejorado += ", close-up shot, 8k, cinematic lighting, photorealistic"
    
    return prompt_mejorado


# Cargar modelo de imagen (El Pintor)
pipe_img = StableDiffusionPipeline.from_pretrained("SG161222/Realistic_Vision_V5.1_noVAE", torch_dtype=torch_dtype)
pipe_img = pipe_img.to(device)

def generar_imagen(prompt_final, nombre_archivo):
    # Parámetros de calidad explicados en la teoría [cite: 174, 175]
    image = pipe_img(
        prompt=prompt_final,
        negative_prompt="cartoon, drawing, anime, deformed, bad anatomy, disfigured, human skin on robot", 
        num_inference_steps=40, # Calidad alta
        guidance_scale=7.0,     # Fidelidad al texto
        height=512, width=512
    ).images[0]
    image.save(nombre_archivo)

async def generar_audio(texto_ingles, nombre_archivo):
    # 1. Traducir al español [cite: 186]
    traductor = GoogleTranslator(source='auto', target='es')
    texto_espanol = traductor.translate(texto_ingles)
    
    # 2. Generar voz neural [cite: 188]
    communicate = edge_tts.Communicate(texto_espanol, 'es-ES-AlvaroNeural')
    await communicate.save(nombre_archivo)


def montar_video(datos_escenas, salida="trailer_acero_puro.mp4"):
    clips = []
    for escena in datos_escenas:
        # Cargamos audio
        audio = AudioFileClip(escena['audio'])
        # Creamos imagen y asignamos duración del audio
        clip = ImageClip(escena['imagen']).set_duration(audio.duration).set_audio(audio)
        # Efecto de transición (crossfade) [cite: 203]
        clip = clip.crossfadein(0.5)
        clips.append(clip)
    
    # Renderizamos
    video_final = concatenate_videoclips(clips, method="compose")
    video_final.write_videofile(salida, fps=24)

async def main():
    # 1. Leemos el guion
    escenas_texto = leer_pdf_y_dividir("input.pdf")
    datos_para_montaje = []

    # 2. Bucle por cada escena [cite: 205]
    for i, texto in enumerate(escenas_texto):
        print(f"Procesando escena {i+1}...")
        
        # El Cerebro piensa
        prompt_base = generar_prompt_base(texto)
        # Inyectamos contexto de Acero Puro
        prompt_final = inyectar_vestuario(texto, prompt_base)
        
        print(f"Prompt Generado: {prompt_final}")
        
        # Nombres de archivos temporales
        archivo_img = f"frame_{i}.png"
        archivo_audio = f"audio_{i}.mp3"
        
        # Generamos Assets
        generar_imagen(prompt_final, archivo_img)
        await generar_audio(texto, archivo_audio)
        
        # Guardamos datos para el editor
        datos_para_montaje.append({
            'imagen': archivo_img,
            'audio': archivo_audio
        })

    # 3. Montaje final
    montar_video(datos_para_montaje)
    print("¡Corte! Película terminada.")

if __name__ == "__main__":
    asyncio.run(main())