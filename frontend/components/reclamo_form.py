import streamlit as st
import requests
from api.client import send_reclamo

def show_reclamo_form():
    """Muestra y maneja el formulario de reclamos"""
    with st.form(key="reclamo_form"):
        foto = st.file_uploader("Subir foto de la incidencia", type=["jpg", "png"])
        ubicacion = st.text_input("Indica la ubicación del problema")
        
        if st.form_submit_button("Enviar Reclamo"):
            handle_reclamo_submission(foto, ubicacion)

def handle_reclamo_submission(foto, ubicacion):
    """Maneja el envío del formulario de reclamo"""
    if foto and ubicacion and st.session_state.cedula:
        try:
            response = send_reclamo(
                cedula=st.session_state.cedula,
                foto=foto,
                ubicacion=ubicacion
            )
            
            if response.status_code == 200:
                handle_successful_reclamo(ubicacion)
            else:
                st.error("Error al registrar el reclamo. Por favor intenta nuevamente.")
                
        except Exception as e:
            st.error(f"Error procesando la imagen: {str(e)}")
    else:
        st.error("Debes subir una foto y proporcionar una ubicación")

def handle_successful_reclamo(ubicacion):
    """Maneja el flujo post-reclamo exitoso"""
    from api.client import enviar_mensaje
    
    respuesta_personalizada = enviar_mensaje(
        f"Genera mensaje de confirmación para ubicación: {ubicacion}. "
        "Tono empático y profesional, incluir referencia a la ubicación."
    )
    
    st.session_state.conversacion.append({
        "usuario": "📸 Envié un reclamo con foto",
        "bot": respuesta_personalizada
    })
    
    st.success("✅ Reclamo registrado exitosamente")
    st.session_state.modo_reclamo = False
    st.rerun()