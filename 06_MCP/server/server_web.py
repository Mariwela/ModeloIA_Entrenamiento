import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importamos tu mcp ya configurado de tu main.py
from server.main import mcp

app = FastAPI(title="Olympic MCP Web Server")

# Requisito de Seguridad/Conectividad: Permitir que clientes como Cherry Studio conecten
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REQUISITO 2 & 7: Endpoint para transporte HTTP (SSE) e integración FastAPI
mcp.handle_fastapi(app)

@app.get("/")
async def root():
    return {"status": "Running", "endpoint": "/sse"}

# REQUISITO 7: Endpoint auxiliar
@app.get("/health")
def health():
    return {
        "status": "online", 
        "transport": "HTTP/SSE",
        "tools": ["medals", "analyze"]
    }