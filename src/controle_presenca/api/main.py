from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .routes import presenca, sessao, alunos

app = FastAPI(
    title="ExpliCAASO API",
    description="API para controle de presença e gestão de alunos",
    version="1.0.0"
)

# Inclui as rotas da API
app.include_router(presenca.router)
app.include_router(sessao.router)
app.include_router(alunos.router)

# Servir arquivos estáticos do frontend
frontend_path = os.path.join(os.path.dirname(__file__), "../../../frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))

# Rota da API (mantém compatibilidade)
@app.get("/api")
def root():
    return {
        "status": "SUCESSO!",
        "mensagem": "A API e o Banco de Dados estão conversando!",
        "versao": "1.0.0"
    }

@app.get("/health")
def health():
    """Endpoint para verificar se a API está funcionando"""
    return {"status": "healthy", "servico": "ExpliCAASO API"}
