import streamlit as st
from session.manager import init_session_state, check_inactivity
from components.chat_interface import show_chat_interface
from components.reclamo_form import show_reclamo_form
from utils.helpers import extraer_cedula
from api.client import enviar_mensaje

# Configuración inicial
st.title("Chatbot Municipal - Gestión de Basura")
init_session_state()
check_inactivity()

# Componente principal de chat
show_chat_interface()

def handle_message_submission(mensaje: str):
    """Maneja el envío de mensajes regulares"""
    if "reclamo" in mensaje or "queja" in mensaje:
        handle_reclamo_intent(mensaje)
    else:
        handle_normal_message(mensaje)

def handle_reclamo_intent(mensaje: str):
    """Maneja la intención de hacer reclamos"""
    if not st.session_state.cedula:
        respuesta = "📝 Para procesar tu reclamo necesitamos verificar tu identidad. Por favor, proporcióname tu número de cédula."
        st.session_state.conversacion.append({
            "usuario": mensaje,
            "bot": respuesta
        })
    else:
        st.session_state.modo_reclamo = True
        
    st.rerun()

def handle_normal_message(mensaje: str):
    """Procesa mensajes no relacionados con reclamos"""
    respuesta = enviar_mensaje(mensaje)
    st.session_state.conversacion.append({
        "usuario": mensaje,
        "bot": respuesta
    })
    st.rerun()

# Lógica de flujo principal
if st.session_state.modo_reclamo:
    show_reclamo_form()
else:
    # Manejo de mensajes normales
    mensaje_usuario = st.text_input("Escribe tu mensaje:", key="input_usuario")
    
    # Detección de cédula
    if not st.session_state.cedula and mensaje_usuario:
        if cedula := extraer_cedula(mensaje_usuario):
            st.session_state.cedula = cedula
    
    if st.button("Enviar") and mensaje_usuario.strip():
        handle_message_submission(mensaje_usuario.strip().lower())