from flask import Flask, abort, request, make_response, jsonify
import requests

from book.dbcon import initialize_db, close_connection, is_book_exists, add_book, get_book_by_id, update_book, \
    delete_book

app = Flask(__name__)


@app.before_first_request
def initialize():
    initialize_db()


@app.teardown_appcontext
def teardown(exception):
    close_connection()


@app.route("/api/book/create_book", methods=['POST'])
def create_book():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'admin':
        abort(401)
    if not request.json:
        abort(406)
    book_data = request.json
    if not book_data.get('name') or not book_data.get('category'):
        abort(406)
    book_name = book_data.get('name')
    book_category = book_data.get('category')
    if is_book_exists(book_name, book_category):
        abort(409)

    try:
        book = add_book(book_name, book_category)
        return jsonify(book)
    except:
        abort(500)


@app.route("/api/book/update_book", methods=['PUT'])
def modify_book():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'admin':
        abort(401)
    if not request.json:
        abort(406)
    book_data = request.json
    if not book_data.get('id') or not book_data.get('name') or not book_data.get('category'):
        abort(406)
    book_id = book_data.get('id')
    book_name = book_data.get('name')
    book_category = book_data.get('category')
    if get_book_by_id(book_id) is None:
        abort(406)
    try:
        update_book(book_id,book_name,book_category)
        return jsonify({})
    except:
        abort(500)


@app.route("/api/book/remove_book", methods=['DELETE'])
def remove_book():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] != 'admin':
        abort(401)
    if not request.json:
        abort(406)
    book_data = request.json
    if not book_data.get('id') :
        abort(406)
    book_id = book_data.get('id')
    if get_book_by_id(book_id) is None:
        abort(406)
    try:
        delete_book(book_id)
        return jsonify({})
    except:
        abort(500)


if __name__ == '__main__':
    app.run(port=8083)
