from pydantic import BaseModel, Field, field_validator

class Cliente(BaseModel):
    cedula: int = Field(..., gt=0, description="La cédula debe ser un número positivo.")
    nombre: str 
    direccion: str 

    @field_validator('cedula')
    def validar_cedula(cls, value):
        if len(str(value)) < 5:
            raise ValueError("La cédula debe tener al menos 5 digitos.")
        return value
    
class Reclamo(BaseModel):
    cedula: int = Field(..., gt=0, description="La cédula debe ser un número positivo.") 
    foto: str  # URL o base64 de la imagen
    ubicacion: str  # Coordenadas o dirección

    @field_validator('cedula')
    def validar_cedula(cls, value):
        if len(str(value)) < 5:
            raise ValueError("La cédula debe tener al menos 5 digitos.")
        return value