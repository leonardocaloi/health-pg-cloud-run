# Usa a imagem oficial do Python versão 3.9 como base
FROM python:3.9

# Define uma variável de ambiente para a porta
ENV PORT 3000

# Atualiza o sistema e instala o pip
RUN apt-get update -y && \
    apt-get install -y python3-pip

# Copia o diretório app (que contém app.py e requirements.txt) para /app no container
COPY app/ /app

# Define /app como o diretório de trabalho
WORKDIR /app

# Instala as dependências Python listadas em requirements.txt
RUN pip install -r requirements.txt

# Instala o Gunicorn, um servidor HTTP WSGI para Python
RUN pip install gunicorn

# Executa o Gunicorn, vinculando-o à variável de ambiente $PORT e especifica que
# o módulo Flask 'app' (dentro de app.py) será usado
CMD exec gunicorn --bind :$PORT main:app