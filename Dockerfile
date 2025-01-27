# Dockerfile
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /core

# Copia os arquivos do projeto
COPY requirements.txt requirements.txt

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto para dentro do contêiner
COPY . /core/

# Expor a porta que o Django vai rodar
EXPOSE 8000

# Comando padrão para executar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
