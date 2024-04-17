from flask import Flask, jsonify
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto
load_dotenv()

app = Flask(__name__)

# Nome da conexão da instância do Cloud SQL (é o que você encontra no Google Cloud Console)
instance_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')

# Obtém as configurações de conexão do banco de dados das variáveis de ambiente
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Caminho do Unix socket fornecido pelo Google Cloud
unix_socket = f'/cloudsql/{instance_connection_name}/.s.PGSQL.5432'

# Monta a URI de conexão ao banco
database_uri = f'postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host={unix_socket}'

# Cria uma engine de conexão ao banco
engine = create_engine(database_uri)

@app.route('/health')
def health_check():
    try:
        # Tentativa de conexão ao banco
        with engine.connect() as connection:
            # Executa uma consulta simples para testar a conexão
            result = connection.execute("SELECT 1")
            # Lê o resultado da consulta
            data = result.fetchone()
            # Verifica se o resultado é o esperado
            if data == (1,):
                return jsonify({"status": "success", "message": "Database connection is healthy"}), 200
    except Exception as e:
        # Em caso de erro, retorna uma mensagem de falha
        return jsonify({"status": "failure", "message": str(e)}), 500

@app.route('/')
def hello_world():
    # Simplesmente retorna uma resposta "Hello, World!"
    return 'Hello, World!'

@app.route('/get_env')
def get_env():
    # Captura todas as variáveis de ambiente e seus valores
    env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    return jsonify(env_vars)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
