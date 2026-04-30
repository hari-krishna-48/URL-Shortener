from flask import Flask, request, jsonify
import os

from jwt import generate_jwt, verify_jwt
from utils import config
import storage

app = Flask(__name__)


@app.route('/users', methods=['POST'])
def create_user():
    data: dict[str, str] = request.get_json(silent=True, force=True) or {}
    username = data['username']
    password = data['password']
    if not storage.create_user(username, password):
        return jsonify("duplicate"), 409
    return jsonify({'username': username}), 201


@app.route('/users', methods=['PUT'])
def update_password():
    data: dict[str, str] = request.get_json(silent=True, force=True) or {}
    username = data['username']
    old_password = data['old-password']
    new_password = data['new-password']
    if not storage.update_password(username, old_password, new_password):
        return jsonify("forbidden"), 403
    return jsonify({'username': username}), 200


@app.route('/users/login', methods=['POST'])
def login():
    data: dict[str, str] = request.get_json(silent=True, force=True) or {}
    username = data['username']
    password = data['password']
    if not storage.verify_password(username, password):
        return jsonify("forbidden"), 403
    token = generate_jwt(username)
    return jsonify({'token': token}), 201


@app.route('/auth/verify', methods=['POST'])
def verify_token():
    data: dict[str, str] = request.get_json(silent=True, force=True) or {}
    token = data.get('token') or request.headers.get('Authorization')
    payload = verify_jwt(token)
    if payload is None:
        return jsonify("forbidden"), 403
    username = payload.get('username')
    if not isinstance(username, str):
        return jsonify("forbidden"), 403
    return jsonify({'payload': payload}), 200

@app.after_request
def add_instance_header(response):
    """Add instance ID to response headers to demo load balancing (only in Docker)"""
    if config.instance_id:
        response.headers['X-Instance-ID'] = config.instance_id
    return response

if __name__ == '__main__':
    # Bind to 0.0.0.0 in Docker, 127.0.0.1 locally
    host = '0.0.0.0' if os.getenv('DOCKER_ENV') == 'true' else '127.0.0.1'
    app.run(host=host, port=8001, debug=True)