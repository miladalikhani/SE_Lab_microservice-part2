import sqlite3
from flask import g

DATABASE = 'books.db'


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
    create table if not exists books
    (
        id integer primary key,
        name text not null,
        category text not null
    );
    """)


def is_book_exists(name, category):
    res = query_db("""
    select * from books
    where name like ?
    and category like ? ;
    """, [name, category], one=True)
    if res is None:
        return False
    return True


def get_book_by_id(id):
    res = query_db("""
    select name, category from books
    where id = ? ;
    """, [id], one=True)
    return res


def update_book(id, name, category):
    query_db("""
    update books set name = ? , category = ?
    where id = ?
    """, [name, category, id], commit=True)


def delete_book(id):
    query_db("""
    delete from books 
    where id = ?
    """, [id], commit=True)

def add_book(name, category):
        query_db("""
        insert into books (name, category)
        values ( ? , ? );
        """, [name, category], commit=True)
        res = query_db("""
        select * from books
        where name like ? 
        and category like ?
        """, [name, category], one=True)
        return res
