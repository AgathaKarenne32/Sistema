 # client_evaluation_service/Dockerfile
    # Imagem base Python 3.11
    FROM python:3.11

    # Define o diretório de trabalho dentro do contêiner
    WORKDIR /app

    # Copia o arquivo de requisitos para o diretório de trabalho
    COPY requirements.txt .

    # Instala as dependências Python. --no-cache-dir para otimizar o tamanho da imagem.
    RUN pip install --no-cache-dir -r requirements.txt

    # Copia todo o código do serviço de avaliação de cliente para o diretório de trabalho
    # (isso inclui main.py, models.py e utils.py, que você copiou para este diretório)
    COPY . .

    # Comando para iniciar o servidor Uvicorn com a aplicação FastAPI
    # Escuta em todas as interfaces (0.0.0.0) na porta 8000
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]