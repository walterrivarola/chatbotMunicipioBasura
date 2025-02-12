from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.openai_service import generar_respuesta_gpt
from app.services.database import agregar_cliente, agregar_reclamo, obtener_clientes, obtener_reclamos, obtener_cliente_por_cedula_gpt, verificar_cedula_gpt
from app.models.schemas import Cliente, Reclamo
from app.core.utils import validar_cedula, guardar_foto, extraer_cedula
from app.services import session_manager
import logging
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
#import time
#import uuid

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # O el nivel que prefieras


# Tiempo de expiración para el token (por ejemplo, 5 minutos)
#TOKEN_EXPIRATION = 300  # en segundos

# Diccionario global para almacenar el contexto de cada conversación
# La estructura es: { token: { "context": List[Dict], "last_active": timestamp, "cedula": int (opcional) } }
#conversation_contexts: Dict[str, Dict[str, Any]] = {}

# Definir un modelo Pydantic para el cuerpo de la solicitud
class MensajeRequest(BaseModel):
    mensaje: str
    cedula: Optional[int] = None
    token: Optional[str] = None

# Elimina los tokens que han expirado.
#def cleanup_expired_tokens():
    
#    now = time.time()
#    expired = [token for token, data in conversation_contexts.items() if now - data["last_active"] > TOKEN_EXPIRATION]
#    for token in expired:
#        del conversation_contexts[token]

# FUNCIONES POST
@router.post("/chat")
async def chat(solicitud: MensajeRequest):
    session_manager.cleanup_expired_tokens()  # Limpia tokens expirados

    mensaje = solicitud.mensaje
    cedula = solicitud.cedula
    token = solicitud.token

    # Si no se envía token o el token no existe en el contexto, se crea uno nuevo
    if token is None or token not in session_manager.conversation_contexts:
        token = session_manager.create_token()
    
    # Actualizar el timestamp de actividad para este token
    session_manager.update_last_active(token)
    context = session_manager.conversation_contexts[token]

    # Verificamos si el usuario está respondiendo con su nombre o dirección
    if "awaiting" in context:
        if context["awaiting"] == "nombre":
            context["nombre"] = mensaje
            context["awaiting"] = "direccion"
            return {"respuesta": "Ahora dime tu dirección para completar tu registro.", "token": token}

        elif context["awaiting"] == "direccion":
            context["direccion"] = mensaje
            context["awaiting"] = None  # Ya no estamos esperando más datos

            # Ahora que tenemos todos los datos, registramos al usuario
            nuevo_cliente = Cliente(
                cedula=context["cedula"],
                nombre=context["nombre"],
                direccion=context["direccion"]
            )
            agregar_cliente(nuevo_cliente)

            return {"respuesta": f"¡Listo {nuevo_cliente.nombre}! Te he registrado en el sistema. ¿En qué puedo ayudarte ahora?", "token": token}

    # Si se recibe una cédula y aún no se ha guardado en el contexto, la asignamos
    if cedula is not None and context["cedula"] is None:
        context["cedula"] = cedula

    # Si ya hay una cédula en el contexto, verificamos y construimos el contexto.
    if context["cedula"] is not None:

        # Aquí se puede agregar la lógica de verificación y la generación del mensaje de sistema, por ejemplo:
        if not verificar_cedula_gpt(context["cedula"]):
            cedula_actual = context["cedula"]
            # Si aún no hemos pedido el nombre, lo solicitamos
            if "nombre" not in context or context["nombre"] is None:
                context["awaiting"] = "nombre"
                return {"respuesta": "No encuentro tu cédula en el sistema. ¿Cuál es tu nombre completo?", "token": token}
            # Si ya tenemos el nombre, pedimos la dirección
            #if "direccion" not in context or context["direccion"] is None:
            #    context["awaiting"] = "direccion"
            #    return {"respuesta": f"Gracias, {context['nombre']}. Ahora dime tu dirección.", "token": token}

            # Si ya tenemos todos los datos, registramos al usuario en la BD
            #nuevo_cliente = Cliente(cedula=cedula_actual, nombre=context["nombre"], direccion=context["direccion"])
            #agregar_cliente(nuevo_cliente)

            # Confirmamos que se registró exitosamente
            #return {"respuesta": f"¡Listo {context['nombre']}! Te he registrado en el sistema con la cédula {cedula_actual}. ¿En qué puedo ayudarte ahora?", "token": token}
        else:
            cliente = obtener_cliente_por_cedula_gpt(context["cedula"])

            # Construir un mensaje de sistema o contexto inicial (solo una vez)
            if not any(msg.get("role") == "system" for msg in context["context"]):
                system_msg = f"Cliente {cliente['nombre']} verificado con cédula {context["cedula"]}."
                context["context"].append({"role": "system", "message": system_msg})

    # Agregar el mensaje del usuario al contexto
    context["context"].append({"role": "user", "message": mensaje})
    
    # Construir el contexto completo (por ejemplo, concatenando todos los mensajes)
    prompt = "\n".join(f"{msg['role']}: {msg['message']}" for msg in context["context"])

    # Generar la respuesta usando la función que tienes (incluyendo el contexto)
    respuesta = generar_respuesta_gpt(mensaje, prompt)

    # Agregar la respuesta del bot al contexto
    context["context"].append({"role": "bot", "message": respuesta.content})
    
    return {"respuesta": respuesta.content, "token": token}


@router.post("/chat-funcional")
async def chat(mensaje: str):
    # Extraer la cédula del mensaje
    cedula = extraer_cedula(mensaje)
    
    # Verificar si el mensaje contiene una cédula
    if cedula:
        if not verificar_cedula_gpt(cedula):
            return {"respuesta": "Lo siento, no estoy encontrando tu número de cédula en el sistema.¿Lo escribiste bien?"}
        cliente = obtener_cliente_por_cedula_gpt(cedula)
        contexto = f"El cliente {cliente['nombre']} está realizando una solicitud."
        respuesta = generar_respuesta_gpt(mensaje, contexto)
    else:
        respuesta = generar_respuesta_gpt(mensaje)
    return {"respuesta": respuesta}

@router.post("/pagar")
async def pagar_servicio(cedula: int):
    if not validar_cedula(cedula):
        raise HTTPException(status_code=400, detail="Cédula inválida. Debe ser un número con al menos 5 dígitos.")
    return {"mensaje": f"Pago procesado para la cedula {cedula}"}



@router.post("/guardar-reclamo")
async def hacer_reclamo(cedula: int, foto: UploadFile = File(...), ubicacion: str = Form(...)):
    if not validar_cedula(cedula):
        raise HTTPException(status_code=400, detail="Cédula inválida. Debe ser un número con al menos 5 dígitos.")
    try:
        ruta_imagen = guardar_foto(foto)
        logger.debug(f"Imagen guardada en: {ruta_imagen}")
        print(f"Cédula: {cedula}, Ubicación: {ubicacion}")
        reclamo = Reclamo(cedula=cedula, foto=ruta_imagen, ubicacion=ubicacion)
        agregar_reclamo(reclamo)
        return {"mensaje": "Reclamo registrado"}
    except Exception as e:
        logger.exception("Error al guardar el reclamo")
        raise HTTPException(status_code=500, detail="Hubo un error al guardar el reclamo")

@router.post("/nuevo_cliente")
async def nuevo_cliente(cliente: Cliente):
    if not validar_cedula(cliente.cedula):
        raise HTTPException(status_code=400, detail="Cédula inválida. Debe ser un número con al menos 5 dígitos.")
    try:
        agregar_cliente(cliente)
        return {"mensaje": "Reclamo registrado"}
    except Exception as e:
        return e
    
# FUNCIONES GET
@router.get("/clientes")
async def listar_clientes():
    return obtener_clientes()

@router.get("/reclamos")
async def listar_reclamos():
    return obtener_reclamos()