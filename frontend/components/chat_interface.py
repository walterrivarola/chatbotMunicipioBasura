import streamlit as st

def show_chat_interface():
    """Muestra la interfaz de conversación del chat"""
    st.write("### Conversación con el Chatbot")
    for msg in st.session_state.conversacion:
        st.write(f"**Tú:** {msg['usuario']}")
        st.write(f"**Chatbot:** {msg['bot']}")