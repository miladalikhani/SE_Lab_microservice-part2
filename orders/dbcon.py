import sqlite3
from flask import g

DATABASE = 'orders.db'


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if commit:
        get_db().commit()
    return (rv[0] if rv else None) if one else rv


def close_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def initialize_db():
    db = get_db()
    db.execute("""
    create table if not exists orders
    (
        id integer primary key,
        username text not null,
        book_id id not null,
        status text not null
    );
    """)

