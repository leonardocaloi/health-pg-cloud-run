from flask import Flask, jsonify
import sqlalchemy  # Importe o módulo completo
from sqlalchemy.engine import url
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env na raiz do projeto
load_dotenv()

app = Flask(__name__)

def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["DB_USER"]  # e.g. 'my-database-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-database-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    unix_socket_path = os.environ[
        "INSTANCE_UNIX_SOCKET"
    ]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note: Some drivers require the `unix_sock` query parameter to use a different key.
        # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
        ),
        # ...
    )
    return pool


# db = connect_unix_socket()


# @app.route('/health')
# def health_check():
#     try:
#         with db.connect() as connection:
#             result = connection.execute("SELECT 1")
#             data = result.fetchone()
#             if data == (1,):
#                 return jsonify({"status": "success", "message": "Database connection is healthy"}), 200
#     except Exception as e:
#         return jsonify({"status": "failure", "message": str(e)}), 500

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