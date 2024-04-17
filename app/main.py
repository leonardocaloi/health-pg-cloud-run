from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.engine import url
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto
load_dotenv()

app = Flask(__name__)

# Initialize the SQLAlchemy connection engine
def init_unix_connection_engine():
    # Nome da conexão da instância do Cloud SQL (é o que você encontra no Google Cloud Console)
    instance_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    
    # Caminho do Unix socket fornecido pelo Google Cloud
    unix_socket = f'/cloudsql/{instance_connection_name}/.s.PGSQL.5432'

    # Monta a URI de conexão ao banco usando sqlalchemy.engine.url.URL
    connection_url = url.URL(
        drivername="postgresql+psycopg2",
        username=db_user,
        password=db_password,
        database=db_name,
        query={
            "host": unix_socket
        }
    )

    # Cria uma engine de conexão ao banco com o pool preconfigurado
    pool = create_engine(connection_url)

    return pool

# Create the database engine using the function
engine = init_unix_connection_engine()
# ...continuation from the init_unix_connection_engine function

@app.route('/health')
def health_check():
    try:
        app.logger.info("Unix Socket Path: %s", unix_socket)
        app.logger.info("DATABASE_URI: %s", str(engine.url))
        with engine.connect() as connection:
            # Execute a simple query to test the connection
            result = connection.execute("SELECT 1")
            # Read the result of the query
            data = result.fetchone()
            # Verify if the result is as expected
            if data == (1,):
                return jsonify({"status": "success", "message": "Database connection is healthy"}), 200
    except Exception as e:
        # In case of an error, return a failure message
        return jsonify({"status": "failure", "message": str(e)}), 500

@app.route('/')
def hello_world():
    # Simply returns a "Hello, World!" response
    return 'Hello, World!'

@app.route('/db_info')
def db_info():
    # Returns information about the database configuration
    db_config = {
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DB_NAME": db_name,
        "CLOUD_SQL_CONNECTION_NAME": instance_connection_name,
        "Unix Socket Path": unix_socket,
        "DATABASE_URI": str(engine.url)
    }
    return jsonify(db_config)

@app.route('/get_env')
def get_env():
    # Capture all environment variables and their values
    env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    return jsonify(env_vars)

if __name__ == '__main__':
    # The app is configured to run on the IP address 0.0.0.0 listening on the port
    # provided by the PORT environment variable, or 80 if not set.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
