# Usa a imagem base do Python com Alpine
FROM python:3.9-alpine

# Define a porta padrão
ENV PORT 3000

# Instala as dependências necessárias para compilar pacotes Python quando necessário
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Copia a aplicação para o container
COPY app/ /app

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências da aplicação, incluindo gunicorn
RUN pip install -r requirements.txt gunicorn

# Configura o comando para iniciar a aplicação via Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 3600 main:app
