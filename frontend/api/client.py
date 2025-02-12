import requests
import streamlit as st

BACKEND_URL = 'http://172.30.128.90:8000'

def enviar_mensaje(mensaje: str):
    """Envía mensajes al endpoint del chatbot"""
    payload = {
        "mensaje": mensaje,
        "cedula": st.session_state.cedula,
        "token": st.session_state.get("token")
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data.get("token")
            return data["respuesta"]
        return "Error en el servidor"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def send_reclamo(cedula: int, foto, ubicacion: str):
    """Envía reclamos al endpoint correspondiente"""
    files = {"foto": (foto.name, foto.getvalue())}
    data = {"cedula": cedula, "ubicacion": ubicacion}
    return requests.post(f"{BACKEND_URL}/registrar-reclamo", files=files, data=data)