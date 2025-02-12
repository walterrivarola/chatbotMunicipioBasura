import streamlit as st
import requests
import time
import re
#from dotenv import load_dotenv
#import os

# Cargar variables de entorno
#load_dotenv()

# Configurar la URL del backend (FastAPI)
BACKEND_URL = 'http://172.30.128.90:8000'

# Titulo de la aplicación
st.title("Chatbot Municipal - Gestión de Basura")

# Inicializar el estado de la sesión usando notación de diccionario para evitar conflictos
if "conversacion" not in st.session_state or not isinstance(st.session_state["conversacion"], list):
    st.session_state["conversacion"] = []

if "cedula" not in st.session_state:
    st.session_state["cedula"] = None

if "ultima_actividad" not in st.session_state:
    st.session_state.ultima_actividad = time.time()

# Control de inactividad: si han pasado más de 180 segundos, reinicia la sesión.
if time.time() - st.session_state["ultima_actividad"] > 180:
    st.session_state["conversacion"] = []
    st.session_state["cedula"] = None
    st.write("Conversación reiniciada. Empiece uno nuevo")
st.session_state["ultima_actividad"] = time.time()

st.write("### Conversación con el Chatbot")

# Mostrar la conversación almacenada en el estado de la sesión
for msg in st.session_state.conversacion:
    st.write(f"**Tú:** {msg['usuario']}")
    st.write(f"**Chatbot:** {msg['bot']}")

# Entrada de texto del usuario
mensaje_usuario = st.text_input("Escribe tu mensaje:", key="input_usuario")

def extraer_cedula_text(texto):
    coincidencias = re.findall(r'\b\d{5,10}\b', texto)
    return coincidencias[0] if coincidencias else None

# Actualizar la cédula si no se ha guardado y el mensaje contiene un número.
if not st.session_state["cedula"] and mensaje_usuario:
    posible_cedula = extraer_cedula_text(mensaje_usuario)
    if posible_cedula:
        st.session_state["cedula"] = int(posible_cedula)
        #st.success(f"Cedula {posible_cedula} detectada y guardada")

# Funcion para enviar mensajes al backend
def enviar_mensaje(mensaje: str):
    payload = {"mensaje": mensaje}
    if st.session_state.get("cedula"):
        payload["cedula"] = st.session_state["cedula"]
    if st.session_state.get("token"):
        payload["token"] = st.session_state["token"]
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json=payload)
        if response.status_code == 200:
            # Guarda (o actualiza) el token recibido en la respuesta
            data = response.json()
            st.session_state["token"] = data.get("token")
            return data["respuesta"]
        else:
            return "Error al comunicarse con el backend."
    except Exception as e:
        return f"Error: {str(e)}"

# Botón para enviar mensaje
if st.button("Enviar"):
    if mensaje_usuario.strip(): # Verificar que el mensaje no esté vacío
        #Enviar mensaje al backend y obtener respuesta
        respuesta_bot = enviar_mensaje(mensaje_usuario.strip())
        
        # Guardar la conversación en el estado de la sesión
        st.session_state.conversacion.append({
            "usuario": mensaje_usuario.strip(),
            "bot": respuesta_bot
        })
        
        # Limpiar la entrada de texto
        #st.session_state.input_usuario = ""

        # Forzar la actualización de la interfaz
        st.rerun()