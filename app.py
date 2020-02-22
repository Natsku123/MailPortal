from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from modules.utils import get_config
from modules.database import handle_login

config = get_config()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config['secret']
jwt = JWTManager(app)


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify({"status": "Missing username."}), 400
    if not password:
        return jsonify({"status": "Missing password."}), 400
    if not handle_login(username, password):
        return jsonify({"status": "Invalid username and/or password."}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route('/')
def root():
    return '# TODO add documentation'


if __name__ == '__main__':
    app.run()
