from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from modules.utils import get_config
from modules.database import (
    handle_login,
    get_users,
    get_user,
    update_user,
    delete_user,
    create_user
)

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
    # TODO add documentation
    return '# TODO add documentation'


@app.route('/users', methods=['GET'])
@jwt_required
def users():
    return jsonify(get_users())


@app.route('/users/add', methods=['POST'])
@jwt_required
def add_user():
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400
    if 'email' not in request.json or 'password' not in request.json or 'domain_id' not in request.json:
        return jsonify({"status": "Missing parameters!"}), 400
    return jsonify(create_user((request.json['email'], request.json['password'], request.json['domain_id'])))


@app.route('/users/<string:email>', methods=['GET'])
@jwt_required
def user(email):
    return jsonify(get_user(email))


@app.route('/users/<string:email>/edit', methods=['POST'])
@jwt_required
def edit_user(email):
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400

    user_obj = get_user(email).get("user", None)
    if not user:
        return jsonify({"status": "User not found."}), 404

    if 'email' in request.json and 'password' in request.json:
        return jsonify(update_user(user_obj['id'], email=request.json['email'], password=request.json['password']))
    elif 'email' in request.json:
        return jsonify(update_user(user_obj['id'], email=request.json['email']))
    elif 'password' in request.json:
        return jsonify(update_user(user_obj['id'], password=request.json['password']))
    else:
        return jsonify({'status': "no changes"})


@app.route('/users/<string:email>/remove', methods=['POST'])
@jwt_required
def remove_user(email):
    user_obj = get_user(email).get("user", None)
    if user_obj:
        return jsonify(delete_user(user_obj['id']))
    else:
        return jsonify({"status": "user doesn't exist"}), 404


if __name__ == '__main__':
    app.run()
