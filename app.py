import os
import base64
import streamlit as st
from openai import OpenAI

# 1. Configuración de página
st.set_page_config(
    page_title="Análisis Neon Vision 🤖",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Estilos Neón Cyberpunk (CSS)
st.markdown("""
    <style>
    /* Fondo oscuro principal */
    .stApp {
        background-color: #0A0E17 !important;
        color: #E2E8F0 !important;
    }

    /* Ocultar elementos nativos innecesarios */
    #MainMenu, footer, header {visibility: hidden;}

    /* Título con resplandor Neón Cian */
    .neon-title {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        color: #00F0FF;
        text-shadow: 0 0 10px #00F0FF, 0 0 20px #00F0FF, 0 0 40px #0077FF;
        margin-bottom: 0.5rem;
    }

    /* Contenedor del GIF animado con marco neón */
    .gif-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    
    .gif-container img {
        border-radius: 16px;
        border: 2px solid #00F0FF;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
    }

    /* Tarjetas y contenedores con bordes Neón */
    div[data-testid="stExpander"], div[data-testid="stFileUploader"] {
        background-color: #121826 !important;
        border: 2px solid #FF007F !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.4) !important;
    }

    /* Botón con efecto neón verde/cian */
    div.stButton > button {
        width: 100%;
        background: transparent !important;
        color: #00FF66 !important;
        border: 2px solid #00FF66 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        text-shadow: 0 0 8px #00FF66 !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.3) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div.stButton > button:hover {
        background-color: #00FF66 !important;
        color: #0A0E17 !important;
        box-shadow: 0 0 25px rgba(0, 255, 102, 0.8) !important;
        transform: scale(1.02);
    }

    /* Estilo de los campos de texto e inputs */
    input, textarea {
        background-color: #1A202C !important;
        color: #00F0FF !important;
        border: 1px solid #00F0FF !important;
        border-radius: 8px !important;
    }

    /* Subtítulos y Labels */
    label, p {
        color: #E2E8F0 !important;
    }

    /* Cajas de respuesta y errores */
    .stAlert {
        background-color: #181E2A !important;
        border: 1px solid #00F0FF !important;
        color: #00F0FF !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Función para codificar la imagen a base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Encabezado principal
st.markdown('<h1 class="neon-title">👁️ NEON VISION: ANALYZER 🤖</h1>', unsafe_allow_html=True)

# GIF Animado de Perrito Neón / Divertido
st.markdown("""
    <div class="gif-container">
        <img src="https://media.giphy.com/media/m3864rB22UYQDBS25X/giphy.gif" width="230">
    </div>
""", unsafe_allow_html=True)

# Input para la API Key de OpenAI o recuperación desde Secrets
secret_key = st.secrets.get("OPENAI_API_KEY", "")
ke = st.text_input('🔑 Ingresa tu Clave de OpenAI', value=secret_key, type="password", help="Pega aquí tu sk-...")

api_key = ke if ke else secret_key

# Cargar la imagen
uploaded_file = st.file_uploader("📂 Sube una imagen para analizar", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("🖼️ Vista Previa de la Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle para detalles adicionales
show_details = st.toggle("💬 ¿Quieres hacer una pregunta específica sobre la imagen?", value=False)
additional_details = ""

if show_details:
    additional_details = st.text_area(
        "Escribe tu pregunta o contexto aquí:",
        placeholder="Ej: ¿Qué ropa lleva puesta la persona? / ¿Qué texto dice el cartel?"
    )

# Botón de análisis
analyze_button = st.button("⚡ ANALIZAR IMAGEN ⚡", type="primary")

# Procesamiento
if analyze_button:
    if not uploaded_file:
        st.warning("⚠️ Por favor, sube una imagen primero.")
    elif not api_key:
        st.warning("⚠️ Ingresa tu API Key de OpenAI para continuar.")
    else:
        try:
            with st.spinner("🌌 Escaneando matriz de píxeles..."):
                client = OpenAI(api_key=api_key)
                base64_image = encode_image(uploaded_file)
                
                prompt_text = "Describe detalladamente lo que ves en esta imagen en español."
                if show_details and additional_details:
                    prompt_text = f"Responde a la siguiente consulta sobre la imagen en español:\n{additional_details}"

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ]

                full_response = ""
                message_placeholder = st.empty()
                
                for completion in client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1200,
                    stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        message_placeholder.markdown(
                            f'<div class="stAlert">{full_response}▌</div>', 
                            unsafe_allow_html=True
                        )
                
                message_placeholder.markdown(
                    f'<div class="stAlert"><strong>🤖 Análisis Neón Completo:</strong><br><br>{full_response}</div>', 
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar la solicitud: {e}")
