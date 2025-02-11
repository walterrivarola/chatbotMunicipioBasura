from fastapi import UploadFile
import shutil
from typing import Optional
import re
#from app.services.database import DATABASE_PATH

def validar_cedula(cedula: int) -> bool:
    """
    Valida que la cédula sea un número entero positivo con al menos 5 dígitos.
    """
    if not isinstance(cedula, int):
        return False
    if cedula <= 0:
        return False
    if len(str(cedula)) < 5:
        return False
    return True

# Funcion para almacenar las fotos en almacenamiento local
def guardar_foto(foto: UploadFile) ->str:
    # Guardar la imagen en la carpeta uploads
    ruta_imagen = f"app/uploads/{foto.filename}"
    with open(ruta_imagen, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)
    return ruta_imagen

def extraer_cedula(mensaje: str) -> Optional[int]:
    # Buscar una secuencia de 10 dígitos en el mensaje
    coincidencias = re.findall(r"\b\d{5,10}\b", mensaje)
    if coincidencias:
        return int(coincidencias[0])  # Retorna la primera cédula encontrada
    return None
