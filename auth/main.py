from flask import Flask, abort, request, make_response, jsonify
import requests
import jwt

from auth.dbcon import check_user, user_exists, create_auth_user, delete_auth_user, close_connection, initialize_db

secret_key = "very_secret"

app = Flask(__name__)

create_profile_endpoint = "http://localhost:8082/api/profile/create_profile"


@app.before_first_request
def initialize():
    initialize_db()


@app.teardown_appcontext
def teardown(exception):
    close_connection()


@app.route("/auth/login", methods=['POST'])
def login():
    if not request.json:
        abort(401)
    user_data = request.json
    if not user_data.get('username') or not user_data.get('password'):
        abort(401)
    username = user_data.get('username')
    password = user_data.get('password')
    status = check_user(username, password)
    if status[0]:
        role = status[1]
        token = jwt.encode(
            payload={"username": username,
                     "role": role},
            key=secret_key,
            algorithm="HS256"
        )
        response = make_response(jsonify({}))
        response.headers['token'] = token
        return response
    else:
        abort(401)


@app.route("/auth/authenticate")
def authenticate():
    if 'token' not in request.headers:
        abort(401)
    token = request.headers['token']
    try:
        data = jwt.decode(
            jwt=token,
            key=secret_key,
            algorithms=["HS256"]
        )
    except:
        abort(401)
    if 'username' not in data or 'role' not in data:
        abort(401)
    return jsonify({"username": data['username'], "role": data["role"]}), 200


@app.route('/auth/signup', methods=['POST'])
def signup():
    if not request.json:
        abort(406)
    user_data = request.json
    if not user_data.get('username') or not user_data.get('password') \
            or not user_data.get('first_name') or not user_data.get('last_name'):
        abort(406)
    username = user_data.get('username')
    password = user_data.get('password')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    if user_exists(username):
        abort(409)
    if create_auth_user(username, password):
        user_profile = {'username': username, 'first_name': first_name, 'last_name': last_name}

        try:
            create_profile_response = requests.post(create_profile_endpoint, json=user_profile)
        except:
            delete_auth_user(username, password)
            abort(500)
        if (create_profile_response.status_code not in [200, 201]):
            delete_auth_user(username, password)
            abort(create_profile_response.status_code)
        return jsonify({})
    else:
        abort(500)


if __name__ == '__main__':
    app.run(port=8081)
