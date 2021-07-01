import json
from flask import Flask, abort, request, make_response, jsonify
import requests
from circuitbreaker import circuit

app = Flask(__name__)

endpoints = []


@app.before_first_request
def load_endpoints():
    endpoints_file = open('endpoints.json')
    data = json.load(endpoints_file)
    endpoints_file.close()
    global endpoints
    endpoints = data

@circuit
def send_request(endpoint, headers):
    if request.method == 'GET':
        res = requests.get(endpoint, headers=headers)
        return res
    elif request.method == 'POST':
        res = requests.post(endpoint, headers=headers, json=request.json)
        return res


def authenticate():
    if 'token' not in request.headers:
        res = make_response(jsonify({}))
        res.status_code = 401
        return res
    auth_endpoint = endpoints["auth/authenticate"]
    res = requests.get(auth_endpoint,headers=request.headers)
    return res

@app.route('/')
def hello():
    return "hello world"


@app.route('/<path:path>', methods=['GET', 'POST'])
def gateway(path):
    global endpoints
    if path in endpoints:
        endpoint = endpoints[path]
        headers = {}
        auth_res = authenticate()
        if auth_res.status_code in [200, 201]:
            headers['username'] = auth_res.json()['username']
        for k, v in request.headers:
            headers[k] = v
        try:
            response = send_request(endpoint, headers)
        except:
            abort(500)
        if response.status_code not in [200, 201]:
            abort(response.status_code)
        res = make_response(jsonify(response.json()))
        if 'token' in response.headers:
            res.headers['token'] = response.headers['token']
        return res
    else:
        abort(404)


if __name__ == '__main__':
    app.run(port=8080)
