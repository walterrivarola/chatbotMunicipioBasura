import time
import uuid
from typing import Dict, Any

# Tiempo de expiración para el token (por ejemplo, 5 minutos)
TOKEN_EXPIRATION = 300 # en segundos

# Diccionario global para almacenar el contexto de cada conversación.
'''
La estructura es:
{
    token: {
        "context": List[Dict[str, Any]], "last_active": timestamp,
        "cedula", int(opcioinal)
    }
}
'''
conversation_contexts: Dict[str, Dict[str, Any]]={}

def create_token() -> str:
    # Crea un nuev token y lo inicializa con un contexto vacío.
    token = str(uuid.uuid4())
    conversation_contexts[token] = {
        "context": [],
        "last_active": time.time(),
        "cedula": None
    }
    return token

def update_last_active(token: str) -> None:
    # Actualiza el timestamp de actividad para el token dado.
    if token in conversation_contexts:
        conversation_contexts[token]["last_active"] = time.time()

def cleanup_expired_tokens() -> None:
    # Elimina los tokens que han expirado.
    now = time.time()
    # Sólo eliminar los tokens cuyo tiempo inactivo supera TOKEN_EXPIRATION
    expired_tokens = [
        token for token, data in conversation_contexts.items()
        if now - data["last_active"] > TOKEN_EXPIRATION
        ]
    for token in expired_tokens:
        del conversation_contexts[token]

def get_context(token: str) -> Dict[str, Any]:
    # Devuelve el contexto de la conversación para el token,
    # o None si no existe.
    return conversation_contexts.get(token)