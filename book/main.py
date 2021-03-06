from flask import Flask, abort, request, make_response, jsonify
import requests

from book.dbcon import initialize_db, close_connection, is_book_exists, add_book, get_book_by_id, update_book, \
    delete_book, get_books_of_category, find_book

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
    if not book_data.get('name') or not book_data.get('category') or not book_data.get('price'):
        abort(406)
    book_name = book_data.get('name')
    book_category = book_data.get('category')
    book_price = book_data.get('price')
    if is_book_exists(book_name, book_category):
        abort(409)
    try:
        book = add_book(book_name, book_category, book_price)
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
    if not book_data.get('id') or not book_data.get('name') or not book_data.get('category') or \
            not book_data.get(
            'price'):
        abort(406)
    book_id = book_data.get('id')
    book_name = book_data.get('name')
    book_category = book_data.get('category')
    book_price = book_data.get('price')
    if get_book_by_id(book_id) is None:
        abort(406)
    try:
        update_book(book_id, book_name, book_category, book_price)
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
    if not book_data.get('id'):
        abort(406)
    book_id = book_data.get('id')
    if get_book_by_id(book_id) is None:
        abort(406)
    try:
        delete_book(book_id)
        return jsonify({})
    except:
        abort(500)


@app.route("/api/book/books_of_category")
def view_books_of_category():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] not in ('admin', 'user'):
        abort(401)
    if 'category' not in request.args:
        abort(406)
    category = request.args.get('category')
    books = get_books_of_category(category)
    return jsonify(books)


@app.route("/api/book/search")
def search_for_book():
    headers = request.headers
    if 'username' not in headers or 'role' not in headers:
        abort(401)
    if headers['role'] not in ('admin', 'user'):
        abort(401)
    name = ""
    if 'q' in request.args:
        name = request.args.get('q')
    books = find_book(name)
    return jsonify(books)


@app.route("/api/book/check")
def check_book():
    if not request.args:
        abort(406)
    if 'book_id' not in request.args:
        abort(406)

    book_id = request.args['book_id']
    try:
        res = get_book_by_id(book_id)
        if res is None:
            return jsonify({'status': False})
        res_json = {'status': True, 'id': book_id, 'name': res['name'], 'category': res['category'],
                    'price': res['price']}
        return jsonify(res_json)
    except:
        abort(500)


if __name__ == '__main__':
    app.run(port=8083)
