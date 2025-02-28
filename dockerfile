# Use a imagem base oficial do Python 3.12
FROM python:3.12-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos de requisitos
COPY requirements.txt requirements.txt

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Criar o diretório para os arquivos dentro do container
RUN mkdir -p /app/arquivospdfs

# Copie todos os arquivos da aplicação
COPY . .

# Exponha as portas necessárias
EXPOSE 8000  
EXPOSE 8501  

# Definir o volume para persistência dos arquivos
VOLUME ["/app/arquivospdfs"]

# Comando para rodar FastAPI e Streamlit ao mesmo tempo
CMD ["sh", "-c", "uvicorn endpoint:app --host 0.0.0.0 --port 8000 & streamlit run frontend_1.py --server.port 8501 --server.address 0.0.0.0"]
