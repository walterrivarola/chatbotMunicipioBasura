from openai import OpenAI
from app.core.config import settings

# Inicializa el cliente con la API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generar_respuesta_gpt(mensaje: str, contexto: str = None) -> str:
    # Definir el contexto inicial del sistema
    sistema = """
    Eres un asistente para la gestión del servicio de basura de un municipio.
    Tu objetivo es guiar al usuario a través de los siguientes flujos:
    1. Pago del servicio.
    2. Registro de reclamo.
    3. Registro de nuevo cliente.
    Siempre debes solicitar la cédula del usuario y verificar si existe en el sistema.
    """

    # Agregar contexto adicional si es necesario
    if contexto:
        sistema += contexto

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sistema},
            {"role": "user", "content": mensaje}
        ]
    )
    return response.choices[0].message