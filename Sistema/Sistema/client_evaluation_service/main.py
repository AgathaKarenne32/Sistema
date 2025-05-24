cat > client_evaluation_service/main.py << 'EOF'
# client_evaluation_service/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx # Importa a biblioteca httpx para fazer requisições HTTP assíncronas

# Importa os modelos e utilitários.
# Certifique-se de que models.py e utils.py estejam no mesmo diretório ou acessíveis via PYTHONPATH.
from models import Cliente, Resposta
from utils import jsonc

# Configuração da URL do Serviço de ML Model Serving.
# 'ml_model_service' é o nome do serviço definido no docker-compose.yml,
# que o Docker Compose resolve para o IP interno do contêiner.
# A porta 8001 é a porta que o serviço de ML estará escutando.
ML_MODEL_SERVICE_URL = "http://ml_model_service:8001" 

# Mapeamento de clusters para respostas textuais.
# Este dicionário permanece neste serviço, pois ele é responsável por formatar a resposta final.
respostas = {
    0: "São clientes que possuem grandes limites totais no cartão, mas não são bons pagadores, logo, não têm muito limite disponível.",
    1: "Clientes que gastam muito com saques. Compram pouco no crédito e são bons pagadores.",
    2: "Clientes com maior preferência em usar débito e saques ao invés do crédito.",
    3: "São os clientes que menos utilizam os serviços financeiros.",
    4: "Utilizam muito o serviço de crédito e são bons pagadores."
}

# Inicializa a aplicação FastAPI.
app = FastAPI()

# Definições de CORS para permitir requisições do frontend.
# Permite todas as origens por simplicidade, mas em produção, especifique as origens permitidas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

# Endpoint de saúde para verificar se o serviço está funcionando.
@app.get("/health")
def read_health():
    return {"status": "client_evaluation_service funcionando"}

# Endpoint principal para avaliação de cliente.
# Recebe os dados do cliente do frontend e os envia para o serviço de ML.
@app.post("/avaliar", response_model=Resposta)
async def avaliacao(cliente: Cliente):
    print(f"Iniciando a avaliação para o cliente: {cliente.name}")
    try:
        # Prepara os dados para enviar ao Serviço de ML.
        # A API do serviço de ML espera apenas os dados numéricos para predição.
        ml_input_data = {
            "balance": cliente.balance,
            "purchases": cliente.purchases,
            "cash_advance": cliente.cash_advance,
            "credit_limit": cliente.credit_limit,
            "payments": cliente.payments
        }

        # Faz uma requisição HTTP POST assíncrona para o Serviço de ML Model Serving.
        # Usa httpx.AsyncClient para garantir que a requisição seja não bloqueante.
        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(f"{ML_MODEL_SERVICE_URL}/predict", json=ml_input_data)
            response.raise_for_status() # Lança uma exceção se o status da resposta for um erro (4xx ou 5xx)
            prediction_result = response.json() # Pega a resposta JSON do serviço de ML

        # Extrai o ID do cluster da resposta do serviço de ML.
        cluster_id = prediction_result.get("cluster")
        if cluster_id is None:
            raise ValueError("O Serviço de ML Model Serving não retornou um ID de cluster válido.")

        # Constrói o objeto de resposta final com base no cluster previsto e nas respostas pré-definidas.
        resp = {
            "nome": cliente.name,
            "cluster": cluster_id,
            "resposta": respostas.get(cluster_id, "Cluster desconhecido.") # Garante uma resposta padrão se o cluster não for encontrado
        }
        r = Resposta(**resp)
        print(f"Resultado para {cliente.name}: {r.resposta}")
        return jsonc(r) # Retorna a resposta formatada usando a função jsonc
    except httpx.RequestError as exc:
        # Captura erros de conexão (ex: serviço de ML não está rodando ou acessível).
        print(f"Erro ao se comunicar com o serviço de ML: {exc}")
        raise HTTPException(status_code=500, detail=f"Não foi possível conectar ao serviço de avaliação de ML. Erro: {exc}")
    except httpx.HTTPStatusError as exc:
        # Captura erros de status HTTP retornados pelo serviço de ML.
        print(f"Erro do serviço de ML: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(status_code=500, detail=f"Erro no serviço de avaliação de ML. Status: {exc.response.status_code}")
    except Exception as e:
        # Captura quaisquer outros erros inesperados durante o processo.
        print(f"Erro inesperado na avaliação: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado durante a análise: {e}")
EOF