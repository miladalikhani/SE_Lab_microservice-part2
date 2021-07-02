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

if __name__ == '__main__':
    app.run(port=8084)
