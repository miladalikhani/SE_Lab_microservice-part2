from flask import Flask, abort, request, make_response, jsonify
import requests

from orders.dbcon import submit_new_order, initialize_db, close_connection

app = Flask(__name__)


mesh_endpoint = "http://localhost:8090/mesh"

@app.before_first_request
def initialize():
    initialize_db()


@app.teardown_appcontext
def teardown(exception):
    close_connection()

@app.route("/api/orders/submit_order", methods=['POST'])
def submit_order():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'user':
        abort(401)
    if not request.json:
        abort(406)

    order_data = request.json
    if not order_data.get('book_id'):
        abort(406)

    username = headers['username']
    book_id = order_data.get('book_id')

    mesh_header = {'token': 'mesh', 'request': 'is_book_exists'}
    res = requests.get(mesh_endpoint, headers=mesh_header, params={'book_id': book_id})
    if res.status_code not in [200, 201]:
        abort(res.status_code)
    if not res.json()['status']:
        abort(406)
    try:
        submit_new_order(username, book_id)
        return jsonify({})
    except:
        abort(500)


if __name__ == '__main__':
    app.run(port=8084)
