from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.engine import url

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto
load_dotenv()

app = Flask(__name__)

def init_unix_connection_engine():
    # Configurações do pool de conexões do banco de dados
    db_config = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_timeout': 30,  # 30 segundos
        'pool_recycle': 1800,  # 30 minutos
    }
    
    # Nome da conexão da instância do Cloud SQL (é o que você encontra no Google Cloud Console)
    instance_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')

    # Configurações para conectar com o Unix Socket fornecido pelo Google Cloud SQL
    unix_socket = f'/cloudsql/{instance_connection_name}'
    db_url = url.URL(
        drivername="postgres+pg8000",
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        query={
            'unix_sock': f"{unix_socket}/.s.PGSQL.5432"
        }
    )

    # Cria uma engine de conexão ao banco com as configurações especificadas
    engine = sqlalchemy.create_engine(db_url, **db_config)
    engine.dialect.description_encoding = None
    return engine

# Inicializa a conexão com o banco de dados
db = init_unix_connection_engine()

@app.route('/health')
def health_check():
    try:
        with db.connect() as connection:
            result = connection.execute("SELECT 1")
            data = result.fetchone()
            if data == (1,):
                return jsonify({"status": "success", "message": "Database connection is healthy"}), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/get_env')
def get_env():
    # Capture all environment variables and their values
    env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    return jsonify(env_vars)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
