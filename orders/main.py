from flask import Flask, abort, request, make_response, jsonify
import requests

from orders.dbcon import submit_new_order, initialize_db, close_connection, view_user_orders, view_all_orders, \
    get_order_by_id, change_order_status

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
        book_name = res.json()['name']
        price = res.json()['price']
        submit_new_order(username, book_id, book_name, price)
        return jsonify({})
    except:
        abort(500)


@app.route("/api/orders/my_orders")
def view_my_order():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'user':
        abort(401)
    username = headers['username']
    try:
        res = view_user_orders(username)
        return jsonify(res)
    except:
        abort(500)


@app.route("/api/orders/all")
def all_orders():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'admin':
        abort(401)
    try:
        res = view_all_orders()
        return jsonify(res)
    except:
        abort(500)


@app.route('/api/orders/change_order_status', methods=['PUT'])
def change_status():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'admin':
        abort(401)
    if not request.json:
        abort(406)

    data = request.json
    if not data.get('order_id') or not data.get('status'):
        abort(406)

    order_id = data.get('order_id')
    new_status = data.get('status')

    if new_status not in ['submit', 'delivered', 'cancel']:
        abort(406)
    if get_order_by_id(order_id) is None:
        abort(406)

    try:
        change_order_status(order_id, new_status)
        return jsonify({})
    except:
        abort(500)


if __name__ == '__main__':
    app.run(port=8084)
