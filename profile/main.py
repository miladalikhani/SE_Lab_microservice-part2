import json
from flask import Flask, abort, request, jsonify, make_response

app = Flask(__name__)


def get_all_profiles():
    users_profile_file = open("user_profile.json")
    users_profile = json.load(users_profile_file)
    users_profile_file.close()
    return users_profile


def get_user_profile(username):
    users = get_all_profiles()
    for entity in users['users']:
        if entity['username'] == username:
            return True, entity
    return False, {}


def profile_exists(username):
    profiles = get_all_profiles()
    for entity in profiles['users']:
        if entity['username'] == username:
            return True
    return False


def write_new_profile(username, first_name, last_name):
    try:
        users_profile_file = open("user_profile.json", "r+")
        users_profile = json.load(users_profile_file)
        new_user = {}
        new_user['username'] = username
        new_user['first_name'] = first_name
        new_user['last_name'] = last_name
        users_profile['users'].append(new_user)
        users_profile_file.seek(0)
        json.dump(users_profile, users_profile_file)
        users_profile_file.truncate()
        users_profile_file.close()
        return True
    except:
        return False


@app.route('/api/view_profile')
def view_profile():
    headers = request.headers
    if 'username' not in headers:
        abort(401)
    else:
        username = headers['username']
        profile = get_user_profile(username)
        if not profile[0]:
            abort(406)
        else:
            res = make_response(jsonify(profile[1]))
            if 'token' in request.headers:
                res.headers['token'] = request.headers['token']
            return res


@app.route('/api/create_profile', methods=['POST'])
def create_profile():
    if not request.json:
        abort(406)
    user_data = request.json
    if not user_data.get('username') \
            or not user_data.get('first_name') or not user_data.get('last_name'):
        abort(406)
    username = user_data.get('username')
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    if profile_exists(username):
        abort(409)
    if write_new_profile(username, first_name, last_name):
        res = make_response(jsonify({}))
        res.status_code = 200
        return res
    else:
        abort(500)


@app.route('/')
def index():
    abort(404)


if __name__ == '__main__':
    app.run(port=8082)
