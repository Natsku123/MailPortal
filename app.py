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
    create_user,
    create_alias,
    delete_alias,
    get_alias,
    get_aliases,
    update_alias,
    create_domain,
    get_domain,
    get_domains
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
    return '# TODO add documentation', 200


@app.route('/users', methods=['GET'])
@jwt_required
def users():
    return jsonify(get_users()), 200


@app.route('/users/add', methods=['POST'])
@jwt_required
def add_user():
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400
    if 'email' not in request.json or 'password' not in request.json or 'domain_id' not in request.json:
        return jsonify({"status": "Missing parameters!"}), 400
    return jsonify(create_user((request.json['email'], request.json['password'], request.json['domain_id']))), 200


@app.route('/users/<string:email>', methods=['GET'])
@jwt_required
def user(email):
    return jsonify(get_user(email)), 200


@app.route('/users/<string:email>/edit', methods=['POST'])
@jwt_required
def edit_user(email):
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400

    user_obj = get_user(email).get("user", None)
    if not user:
        return jsonify({"status": "User not found."}), 404

    if 'email' in request.json and 'password' in request.json:
        return jsonify(update_user(user_obj['id'], email=request.json['email'], password=request.json['password'])), 200
    elif 'email' in request.json:
        return jsonify(update_user(user_obj['id'], email=request.json['email'])), 200
    elif 'password' in request.json:
        return jsonify(update_user(user_obj['id'], password=request.json['password'])), 200
    else:
        return jsonify({'status': "no changes"}), 200


@app.route('/users/<string:email>/remove', methods=['POST'])
@jwt_required
def remove_user(email):
    user_obj = get_user(email).get("user", None)
    if user_obj:
        return jsonify(delete_user(user_obj['id'])), 200
    else:
        return jsonify({"status": "user doesn't exist"}), 404


@app.route('/aliases', methods=['GET'])
@jwt_required
def aliases():
    return jsonify(get_aliases()), 200


@app.route('/aliases/add', methods=['POST'])
@jwt_required
def add_alias():
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400
    if 'source' not in request.json or 'destination' not in request.json or 'domain_id' not in request.json:
        return jsonify({"status": "Missing parameters!"}), 400
    return jsonify(create_alias((request.json['domain_id'], request.json['source'], request.json['destination']))), 200


@app.route('/aliases/user/<string:destination>', methods=['GET'])
@jwt_required
def user_alias(destination):
    return jsonify(get_alias(destination=destination)), 200


@app.route('/aliases/<string:source>', methods=['GET'])
@jwt_required
def alias(source):
    return jsonify(get_alias(source=source)), 200


@app.route('/aliases/<string:source>/edit', methods=['POST'])
@jwt_required
def edit_alias(source):
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400

    alias_obj = get_alias(source).get("aliases", None)
    if not alias_obj:
        return jsonify({"status": "Alias not found."}), 404

    if 'source' in request.json and 'destination' in request.json:
        return jsonify(update_alias(alias_obj[0]['id'], source=request.json['source'], destination=request.json['destination'])), 200
    elif 'source' in request.json:
        return jsonify(update_alias(alias_obj[0]['id'], source=request.json['source'])), 200
    elif 'destination' in request.json:
        return jsonify(update_alias(alias_obj[0]['id'], destination=request.json['destination'])), 200
    else:
        return jsonify({'status': "no changes"}), 200


@app.route('/aliases/<string:source>/remove', methods=['POST'])
@jwt_required
def remove_alias(source):
    alias_obj = get_alias(source).get("aliases", None)
    if alias_obj:
        return jsonify(delete_alias(alias_obj[0]['id'])), 200
    else:
        return jsonify({"status": "alias doesn't exist"}), 404


@app.route('/domains', methods=['GET'])
@jwt_required
def domains():
    return jsonify(get_domains()), 200


@app.route('/domains/<string:name>', methods=['GET'])
@jwt_required
def domain(name):
    return jsonify(get_domain(name)), 200


@app.route('/domains/create', methods=['POST'])
@jwt_required
def add_domain():
    if not request.is_json:
        return jsonify({"status": "Missing JSON in request."}), 400
    if 'name' not in request.json:
        return jsonify({"status": "Missing parameters!"}), 400
    return jsonify(create_domain(request.json['name'])), 200


if __name__ == '__main__':
    app.run()
