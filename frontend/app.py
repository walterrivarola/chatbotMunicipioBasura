import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar la URL del backend (FastAPI)
BACKEND_URL = 'http://0.0.0.0:8000'

# Titulo de la aplicación
st.title("Chatbot Municipal - Gestión de Basura")

# Inicializar el estado de la sesión
if "conversacion" not in st.session_state:
    st.session_state.conversacion=[]


# Funcion para enviar mensajes al backend
def enviar_mensaje(mensaje: str):
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json={"mensaje": mensaje})
        if response.status_code == 200:
            return response.json()["respuesta"]
        else:
            return "Error al comunicarse con el backend."
    except Exception as e:
        return f"Error: {str(e)}"
    
# Interfaz de chat
st.write("### Conversación con el Chatbot")

# Mostrar la conversación almacenada en el estado de la sesión
for mensaje in st.session_state.conversacion:
    st.write(f"**Tú: {mensaje['usuario']}")
    st.write(f"**Chatbot:** {mensaje['bot']}")

# Entrada de texto del usuario
mensaje_usuario = st.text_input("Escribe tu mensaje:")

# Botón para enviar mensaje
if st.button("Enviar"):
    if mensaje_usuario.strip(): # Verificar que el mensaje no esté vacío
        #Enviar mensaje al backend y obtener respuesta
        respuesta_bot = enviar_mensaje(mensaje_usuario)

        # Guardar la conversación en el estado de la sesión
        st.session_state.conversacion.append({
            "usuario": mensaje_usuario,
            "bot": respuesta_bot
        })
        
        # Limpiar la entrada de texto
        mensaje_usuario = ""

        # Forzar la actualización de la interfaz
        st.experimental_rerun()