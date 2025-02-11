from fastapi import FastAPI
from app.routers import chat

app = FastAPI()
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido al chatbot de gestión de basura"}