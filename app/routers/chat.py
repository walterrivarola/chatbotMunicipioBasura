from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.openai_service import generar_respuesta_gpt
from app.services.database import agregar_cliente, agregar_reclamo, obtener_clientes, obtener_reclamos, obtener_cliente_por_cedula_gpt, verificar_cedula_gpt
from app.models.schemas import Cliente, Reclamo
from app.core.utils import validar_cedula, guardar_foto, extraer_cedula
import logging

router = APIRouter()

# FUNCIONES POST
@router.post("/chat")
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # O el nivel que prefieras

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