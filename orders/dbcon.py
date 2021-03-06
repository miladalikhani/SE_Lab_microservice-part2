import sqlite3
from datetime import datetime

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
        book_name text not null,
        price integer not null,
        checkout_date timestamp not null,
        status text not null
    );
    """)


def submit_new_order(username, book_id, book_name, price):
    query_db("""
        insert into orders (username, book_id, book_name, price, checkout_date, status)
        values ( ? , ? , ? , ? , ? , "submit" );
    """, [username, book_id, book_name, price, datetime.now()], commit=True)

def view_user_orders(username):
    res = query_db("""
    select book_name, price, checkout_date from orders
    where username like ?
    and status not like "cancel"
    order by checkout_date desc;
    """, [username])
    return res

def view_all_orders():
    res = query_db("""
    select id as order_id, username, book_id, book_name, price, status, checkout_date from orders
    order by username, checkout_date desc;
    """, [])
    return res

def change_order_status(order_id, status):
    res = query_db("""
    update orders set status = ? 
    where id = ? ;
    """, [status, order_id], commit=True)

def get_order_by_id(order_id):
    res = query_db("""
    select * from orders
    where id = ? ;
    """, [order_id], one=True)
    return res