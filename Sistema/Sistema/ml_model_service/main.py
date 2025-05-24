# ml_model_service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np # Importa numpy para manipulação de arrays

# Define o esquema de entrada para o modelo de ML.
# Estes são os features que o modelo espera para fazer a predição.
class MLInput(BaseModel):
    balance: float
    purchases: float
    cash_advance: float
    credit_limit: float
    payments: float

# Carrega o Modelo de ML na inicialização do serviço.
# O bloco try-except é crucial para lidar com cenários onde o modelo não é encontrado ou está corrompido.
try:
    # joblib.load() carrega o modelo serializado.
    # O caminho 'modelo_cluster_cartao_credito.pkl' é relativo ao WORKDIR do Dockerfile.
    modelo = joblib.load('modelo_cluster_cartao_credito.pkl')
    print("Modelo de ML carregado com sucesso.")
except Exception as e:
    print(f"Erro ao carregar o modelo de ML: {e}")
    modelo = None # Define como None para indicar que o modelo não foi carregado, útil para o health check.

# Inicializa a aplicação FastAPI.
app = FastAPI()

# Endpoint de saúde para verificar o status do serviço e do modelo.
# Retorna 503 Service Unavailable se o modelo não foi carregado.
@app.get("/health")
def read_health():
    if modelo is None:
        raise HTTPException(status_code=503, detail="ML Model não carregado")
    return {"status": "ml_model_service funcionando", "model_loaded": True}

# Endpoint para prever o cluster do cliente.
# Recebe os dados numéricos do cliente e retorna o ID do cluster previsto.
@app.post("/predict")
async def predict_cluster(data: MLInput):
    # Verifica se o modelo foi carregado antes de tentar fazer a predição.
    if modelo is None:
        raise HTTPException(status_code=503, detail="ML Model não está disponível para predição.")
    try:
        # Prepara os dados para a predição do modelo.
        # O modelo espera uma entrada 2D (ex: [[feature1, feature2, ...]]).
        # np.array cria um array numpy, e .reshape(1, -1) o transforma em uma matriz 2D com uma linha.
        features = np.array([
            data.balance,
            data.purchases,
            data.cash_advance,
            data.credit_limit,
            data.payments
        ]).reshape(1, -1)

        # Realiza a predição usando o modelo carregado.
        k = modelo.predict(features)
        cluster_id = int(k[0]) # Garante que o ID do cluster seja um inteiro padrão

        # Retorna o ID do cluster previsto em um formato JSON.
        return {"cluster": cluster_id}
    except Exception as e:
        # Captura erros que podem ocorrer durante o processo de predição.
        print(f"Erro durante a predição do modelo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na predição do modelo: {e}")
    