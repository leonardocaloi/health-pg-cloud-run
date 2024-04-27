from flask import Flask, jsonify
from database import Database
import os


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/health')
def health_check():
    try:
        Database().health_check()
        return jsonify({"status": "success", "message": "Database connection is healthy"}), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500

@app.route('/get_env')
def get_env():
    env_vars = {key: os.getenv(key) for key in os.environ.keys()}
    return jsonify(env_vars)

@app.route('/init_db', methods=['POST'])
def create_tables():
    try:
        Database().init_db()
        return jsonify({"status": "success", "message": "Database initialized successfully"}), 200
    except Exception as e:
        return jsonify({"status": "failure", "message": str(e)}), 500