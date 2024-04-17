from flask import Flask, jsonify
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.engine import url

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto
load_dotenv()

app = Flask(__name__)

logger = logging.getLogger()

def init_db_connection():
    db_config = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_timeout': 30,
        'pool_recycle': 1800,
    }
    return init_unix_connection_engine(db_config)

def init_unix_connection_engine(db_config):
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="postgres+pg8000",
            username=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME'),
            query={
                'unix_sock': f"/cloudsql/{}/.s.PGSQL.5432".format(
                os.environ.get('CLOUD_SQL_CONNECTION_NAME'),
                )
            }
        ),
        **db_config
    )
    pool.dialect.description_encoding = None
    return pool

db = init_db_connection()

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
