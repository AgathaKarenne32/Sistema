# ml_model_service/Dockerfile
# Imagem base Python 3.11
FROM python:3.11

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do serviço de ML para o diretório de trabalho
COPY . .
# O arquivo do modelo .pkl será montado via docker-compose.yml em tempo de execução,
# então não precisamos copiá-lo aqui no Dockerfile.

# Comando para iniciar o servidor Uvicorn.
# Escuta em todas as interfaces (0.0.0.0) na porta 8001 (porta diferente do serviço de avaliação).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
