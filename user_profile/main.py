import json
from flask import Flask, abort, request, jsonify, make_response

from user_profile.dbcon import initialize_db, close_connection, get_user_profile, profile_exists, write_new_profile, \
    update_profile, get_all_profiles

app = Flask(__name__)

@app.before_first_request
def initialize():
    initialize_db()


@app.teardown_appcontext
def teardown(exception):
    close_connection()

@app.route('/api/profile/view_profile')
def view_profile():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
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


@app.route('/api/profile/create_profile', methods=['POST'])
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


@app.route("/api/profile/update_profile", methods=['PUT'])
def update_user_profile():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if not request.json:
        abort(406)
    user_data = request.json
    if not user_data.get('first_name') or not user_data.get('last_name'):
        abort(406)

    username = headers['username']
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    if not update_profile(username,first_name, last_name):
        abort(500)
    else:
        res = make_response(jsonify({}))
        if 'token' in request.headers:
            res.headers['token'] = request.headers['token']
        return res


@app.route("/api/profile/profiles")
def see_profiles():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'admin':
        abort(401)
    try:
        profiles = get_all_profiles()
        return jsonify(profiles)
    except:
        abort(500)


@app.route('/')
def index():
    abort(404)


if __name__ == '__main__':
    app.run(port=8082)
