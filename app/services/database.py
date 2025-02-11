import sqlite3
from pathlib import Path
from typing import Optional, List
from app.models.schemas import Cliente, Reclamo
from fastapi import HTTPException

# Ruta de la base de datos
DATABASE_PATH = Path("chatbot.db")

# Funcions para crear la base de datos y las tablas si no existen
def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        # Tabla de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                       cedula INTEGER PRIMARY KEY NOT NULL,
                       nombre TEXT NOT NULL,
                       direccion TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reclamos (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       cedula INTEGER NOT NULL,
                       foto TEXT NOT NULL,
                       ubicacion TEXT NOT NULL,
                       FOREIGN KEY (cedula) REFERENCES clientes (cedula)                       
            )
        """)
        conn.commit()
    '''
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula_cliente INTEGER NOT NULL,
                fecha DATETIME NOT NULL,
                pagado BOOLEAN,
                FOREIGN KEY (cedula_cliente) REFERENCES clientes (cedula)
            )
        
        """)
    '''
        

# Funciones para guardar los datos en la base de datos
def agregar_cliente(cliente: Cliente):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (cedula, nombre, direccion)
            VALUES (?,?,?)
        """, (cliente.cedula, cliente.nombre,cliente.direccion))
        conn.commit()

def agregar_reclamo(reclamo: Reclamo):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reclamos (cedula, foto, ubicacion)
                VALUES (?,?,?)
            """, (reclamo.cedula, reclamo.foto, reclamo.ubicacion))
            conn.commit()
            print(f"Reclamo guardado: {reclamo}")
    except sqlite3.Error as e:
        print(f"Error al agregar reclamo: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el reclamo en la base de datos")

def obtener_clientes() -> List[Cliente]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        columns = [column[0] for column in cursor.description]
        clientes = []
        for row in cursor.fetchall():
            cliente_data = dict(zip(columns,row))
            clientes.append(Cliente(**cliente_data))
        return clientes
    
def obtener_reclamos() -> List[Reclamo]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reclamos")
        columns = [column[0] for column in cursor.description]
        reclamos = []
        for row in cursor.fetchall():
            reclamos_data = dict(zip(columns,row))
            reclamos.append(Reclamo(**reclamos_data))
        return reclamos

# USO DE OPENAI PARA VERIFICAR DATOS
def verificar_cedula_gpt(cedula: int) -> bool:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cedula FROM clientes WHERE cedula = ?", (cedula,))
        return cursor.fetchone() is not None

def obtener_cliente_por_cedula_gpt(cedula: int) -> Optional[dict]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE cedula = ?", (cedula,))
        row = cursor.fetchone()
        if row:
            return {"cedula": row[0], "nombre": row[1], "direccion": row[2]}
        return None
# Inicializar la base de datos al importar el módulo
init_db()