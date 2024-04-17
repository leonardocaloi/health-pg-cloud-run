from flask import Flask, jsonify, request
import sqlalchemy
import os


app = Flask(__name__)

def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["DB_USER"]  
    db_pass = os.environ["DB_PASS"]  
    db_name = os.environ["DB_NAME"]  
    unix_socket_path = os.environ["INSTANCE_UNIX_SOCKET"]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
        ),
    )
    return pool


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/get_env')
def get_env():
    # Capture all environment variables and their values
    env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    return jsonify(env_vars)


@app.route('/health')
def health_check():
    try:
        db = connect_unix_socket()
        with db.connect() as connection:
            result = connection.execute(sqlalchemy.sql.text("SELECT 1"))
            data = result.fetchone()
            if data == (1,):
                return jsonify({"status": "success", "message": "Database connection is healthy"}), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500


@app.route('/execute_query')
def execute_query():
    query = request.args.get('query')
    if not query:
        return jsonify({"status": "failure", "message": "No query provided"}), 400
    
    try:
        db = connect_unix_socket()
        with db.connect() as connection:
            result = connection.execute(sqlalchemy.sql.text(query))
            data = result.fetchall()
            result_list = [{column: value for column, value in row.items()} for row in data]
            return jsonify(result_list), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))