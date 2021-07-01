import json
from flask import Flask, abort, request, make_response, jsonify
import requests
import jwt

secret_key = "very_secret"

app = Flask(__name__)

create_profile_endpoint = "http://localhost:8082/api/create_profile"

def get_all_users():
    auth_users_file = open("auth_users.json")
    auth_users = json.load(auth_users_file)
    auth_users_file.close()
    return auth_users


def check_user(username, password):
    auth_users = get_all_users()
    for entity in auth_users['users']:
        if entity['username'] == username:
            if entity['password'] == password:
                return True
            else:
                return False
    return False


def user_exists(username):
    auth_users = get_all_users()
    for entity in auth_users['users']:
        if entity['username'] == username:
            return True
    return False


def create_auth_user(username, password):
    try:
        auth_users_file = open("auth_users.json", "r+")
        auth_users = json.load(auth_users_file)
        new_user = {}
        new_user['username'] = username
        new_user['password'] = password
        auth_users['users'].append(new_user)
        auth_users_file.seek(0)
        json.dump(auth_users, auth_users_file)
        auth_users_file.truncate()
        auth_users_file.close()
        return True
    except:
        return False


def delete_auth_user(username,password):
    try:
        auth_users_file = open("auth_users.json", "r+")
        auth_users = json.load(auth_users_file)
        temp = {"username" : username, "password" : password}
        flag = False
        for entity in auth_users['users']:
            if entity['username'] == username and entity['password'] == password:
                flag = True
        if flag:
            auth_users['users'].remove(temp)
        auth_users_file.seek(0)
        json.dump(auth_users, auth_users_file)
        auth_users_file.truncate()
        auth_users_file.close()
        return True
    except:
        return False


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
    if (status):
        token = jwt.encode(
            payload={"username": username},
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
    if 'username' not in data:
        abort(401)
    return jsonify({"username": data['username']}), 200


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
    if (create_auth_user(username,password)):
        user_profile = {}
        user_profile['username'] = username
        user_profile['first_name'] = first_name
        user_profile['last_name'] = last_name

        try:
            create_profile_response = requests.post(create_profile_endpoint,json=user_profile)
        except:
            delete_auth_user(username, password)
            abort(500)
        if (create_profile_response.status_code not in [200,201]):
            delete_auth_user(username,password)
            abort(create_profile_response.status_code)
        return jsonify({})
    else:
        abort(500)


if __name__ == '__main__':
    app.run(port=8081)
