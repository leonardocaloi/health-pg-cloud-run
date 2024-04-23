from flask import Flask, jsonify, request
import sqlalchemy
import os

from pip._vendor.rich import json

app = Flask(__name__)

def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    db_credentials = json.loads(os.environ['DB_CREDENTIALS'])
    db_user = db_credentials["DB_USER"]
    db_pass = db_credentials["DB_PASS"]
    db_name = db_credentials["DB_NAME"]
    unix_socket_path = db_credentials["INSTANCE_UNIX_SOCKET"]

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
    return 'Hello, Irgo!'


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
            result_list = [{column.key: value for column, value in row.items()} for row in data]
            return jsonify(result_list), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))