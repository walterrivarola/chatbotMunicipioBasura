import re

def extraer_cedula(texto: str) -> int | None:
    """Extrae números de cédula de un texto"""
    coincidencias = re.findall(r'\b\d{5,10}\b', texto)
    return int(coincidencias[0]) if coincidencias else None