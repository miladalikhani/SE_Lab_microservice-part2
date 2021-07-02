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


def send_request(endpoint):
    if request.method == 'GET':
        res = requests.get(endpoint,params=request.args)
        return res
    elif request.method == 'POST':
        res = requests.post(endpoint, json=request.json)
        return res
    elif request.method == 'PUT':
        res = requests.put(endpoint, json=request.json)
        return res
    elif request.method == 'DELETE':
        res = requests.delete(endpoint, json=request.json)
        return res


@app.route('/')
def hello():
    return "hello world"


@app.route('/mesh', methods=['GET', 'POST', 'PUT', 'DELETE'])
def mesh():
    global endpoints
    if 'token' not in request.headers or request.headers['token'] != 'mesh':
        abort(401)
    if 'request' not in request.headers:
        abort(406)
    if request.headers['request'] not in endpoints:
        abort(404)
    endpoint = endpoints[request.headers['request']]
    try:
        response = send_request(endpoint)
    except:
        abort(500)
    if response.status_code not in [200, 201]:
        abort(response.status_code)
    res = make_response(jsonify(response.json()))
    return res

if __name__ == '__main__':
    app.run(port=8090)
