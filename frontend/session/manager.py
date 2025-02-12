import time
import streamlit as st

def init_session_state():
    """Inicializa todos los estados de sesión necesarios"""
    defaults = {
        "conversacion": [],
        "cedula": None,
        "modo_reclamo": False,
        "ultima_actividad": time.time(),
        "token": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def check_inactivity():
    """Reinicia la sesión después de 3 minutos de inactividad"""
    if time.time() - st.session_state.ultima_actividad > 180:
        st.session_state.update({
            "conversacion": [],
            "cedula": None,
            "modo_reclamo": False
        })
        st.write("Conversación reiniciada. Empiece uno nuevo")
    
    st.session_state.ultima_actividad = time.time()