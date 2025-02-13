# Chatbot para Gestión de Residuos Municipales 🗑️🤖

**Chatbot inteligente para asistencia en la gestión de residuos municipales, desarrollado con FastAPI (backend) y Streamlit (frontend), potenciado por OpenAI.**

## 🚀 Funcionalidades principales
- Asistencia inteligente para consultas sobre gestión de residuos
- Crear usuarios nuevos
- Gestionar reclamos de basura

## 📋 Prerrequisitos
- Python 3.9+
- [API Key de OpenAI](https://platform.openai.com/api-keys)
- Git
- virtualenv (recomendado)

## ⚙️ Instalación

### 1. Clonar repositorio
```bash
git clone https://github.com/walterrivarola/chatbotMunicipioBasura.git
cd chatbotMunicipioBasura
```

### Crear entorno virtual
```
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

## Configurar variables de entorno
Crear archivo .env en la raíz del proyecto:
```
OPENAI_API_KEY=tu_api_key_aquí  # Reemplazar con tu clave real
```

### Instalar dependencias
```
# Backend (FastAPI)
pip install -r requirements.txt

# Frontend (Streamlit)
pip install -r requirements-frontend.txt
```

## ▶️ Ejecución
Ejecutar en terminales separados:
### Servidor Backend (FastAPI)
```
uvicorn app.main:app --reload --port 8000
```
### Servidor Frontend (Streamlit)
```
streamlit run app/frontend/chat_interface.py --server.port 8501
```

## 🌐 Acceso
* API Docs: http://localhost:8000/docs
* Interfaz Chat: http://localhost:8501
* Dashboard Admin: http://localhost:8501/admin

## 🔧 Estructura del proyecto
```
chatbotMunicipalBasura/
├── app/
│   ├── core/
│   │   ├── config.py            # Variables de entorno (API keys)
│   │   └── utils.py             # Funciones auxiliares (ej: validar cédula)
│   ├── models/
│   │   └── schemas.py           # Pydantic models para validación
│   ├── routers/
│   │   └── chat.py              # Endpoints de FastAPI
│   ├── services/
│   │   ├── openai_service.py    # Lógica de interacción con GPT-4
│   │   └── database.py          # Mock de base de datos (JSON/SQLite)
│   └── main.py
│── frontend/
│    ├── app.py                  # Punto de entrada principal
│    ├── session/                
│    │   └── manager.py          # Manejo de estado de sesión
│    ├── components/             # Componentes UI reutilizables
│    │   ├── chat_interface.py   # Componente de visualización del chat
│    │   └── reclamo_form.py     # Formulario para reclamos
│    ├── api/                    # Cliente API para comunicación con backend
│    │   └── client.py          
│    └── utils/                  # Funciones utilitarias
│        └── helpers.py          # Inicialización de FastAPI
├── requirements.txt             # Dependencias del backend
├── requirements-frontend.txt    # Dependencias del frontend
└── .env.example                 # Variables de entorno (OpenAI API key)
```

## 🔒 Archivo .env ejemplo
```
# .env.example
OPENAI_API_KEY="sk-tu_api_key_aqui_123"
```

## 📌 Notas importantes
1. Nunca compartas tu API Key en commits
2. El entorno virtual debe estar activo durante el desarrollo
3. Para producción, configurar:
    * Variables de entorno seguras
    * HTTPS
    * Autenticación apropiada
