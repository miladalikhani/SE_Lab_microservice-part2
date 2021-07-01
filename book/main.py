from flask import Flask, abort, request, make_response, jsonify
import requests

from book.dbcon import initialize_db, close_connection, is_book_exists, add_book

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
    if add_book(book_name, book_category):
        res = make_response(jsonify({}))
        res.status = 200
        return res
    else:
        abort(500)


if __name__ == '__main__':
    app.run(port=8083)
