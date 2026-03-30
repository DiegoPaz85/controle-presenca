from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"status": "SUCESSO!", "mensagem": "A API e o Banco de Dados estão conversando!"}
