from models import Cliente, Resposta
# import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import joblib

from utils import jsonc
from models import Resposta

# Carrega o Model
modelo = joblib.load('modelo_cluster_cartao_credito.pkl')

respostas = {
    0: "São clientes que possuem grandes limites totais no cartão, mas não são bons pagadores, logo, não têm muito limite disponível.",
    1: "Clientes que gastam muito com saques. Compram pouco no crédito e são bons pagadores.",
    2: "Clientes com maior preferência em usar débito e saques ao invés do crédito.",
    3: "São os clientes que menos utilizam os serviços financeiros.",
    4: "Utilizam muito o serviço de crédito e são bons pagadores."
}

# Inicia o FastAPI - framework responsável por criar o backend
app = FastAPI()

# Definições de acesso
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)



# Função que calcula o núcleo do usuário
def calc_nucleo(cliente: Cliente) -> Resposta:
    c = [cliente.balance, cliente.purchases, cliente.cash_advance, cliente.credit_limit, cliente.payments]
    k = modelo.predict([c])
    resp = {
        "nome": cliente.name,
        "cluster": k[0],
        "resposta": respostas[k[0]]
    }
    r = Resposta(**resp)
    return r

@app.get("/health")
def read_health():
    return {"status": "funcionando"}

# Endpoint
@app.post("/avaliar")
async def avaliacao(cliente: Cliente):
    print(f"Iniciando a avaliação:{cliente}")
    r = calc_nucleo(cliente)
    print(f"Resultado: {r.resposta}")
    return jsonc(r)

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
