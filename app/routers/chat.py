from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.openai_service import generar_respuesta_gpt
from app.services.database import agregar_cliente, agregar_reclamo, obtener_clientes, obtener_reclamos, obtener_cliente_por_cedula_gpt, verificar_cedula_gpt
from app.models.schemas import Cliente, Reclamo
from app.core.utils import validar_cedula, guardar_foto, extraer_cedula
from app.services import session_manager
from pydantic import BaseModel
from typing import Optional


router = APIRouter()

# Definir un modelo Pydantic para el cuerpo de la solicitud
class MensajeRequest(BaseModel):
    mensaje: str
    cedula: Optional[int] = None
    token: Optional[str] = None

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


@router.post("/registrar-reclamo")
async def hacer_reclamo(cedula: int = Form(...),ubicacion: str = Form(...),foto: UploadFile = File(...)):

    if not validar_cedula(cedula):
        raise HTTPException(status_code=400, detail="Cédula inválida. Debe ser un número con al menos 5 dígitos.")
    try:
        ruta_imagen = guardar_foto(foto)
        reclamo = Reclamo(
            cedula=cedula,
            foto=ruta_imagen,
            ubicacion=ubicacion
            )
        
        agregar_reclamo(reclamo)

        # Generar respuesta personalizada
        respuesta = generar_respuesta_gpt(
            f"El usuario con cédula {cedula} reportó un problema en {ubicacion}. "
            "Generar mensaje de confirmación amigable que incluya la ubicación."
        )
        
        return {
            "mensaje": "Reclamo registrado",
            "respuesta_chat": respuesta.content
        }
    except Exception as e:
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