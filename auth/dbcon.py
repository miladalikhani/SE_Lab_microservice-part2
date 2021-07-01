import sqlite3
from flask import g

DATABASE = 'auth_users.db'


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
    create table if not exists auth_users
    (
        id integer primary key,
        username text not null,
        password text not null,
        role text not null
    );
    """)


def get_all_users():
    auth_users = query_db("""
        select * from auth_users;
    """)
    return auth_users


def check_user(username, password):
    auth_users = get_all_users()
    for entity in auth_users:
        if entity['username'] == username:
            if entity['password'] == password:
                if entity['role'] == "user":
                    return True, "user"
                elif entity['role'] == "admin":
                    return True, "admin"
            else:
                return False, None
    return False, None


def user_exists(username):
    auth_users = get_all_users()
    for entity in auth_users:
        if entity['username'] == username:
            if entity['role'] == "user":
                return True
    return False


def create_auth_user(username, password):
    try:
        query_db("""
        insert into auth_users(username, password, role) 
        values (?, ?, "user");
        """, [username, password], commit=True)
        return True
    except:
        return False


def delete_auth_user(username, password):
    try:
        query_db("""
        delete from auth_users
        where username like ?
        and password like ?
        and role like "user";
        """, [username, password], commit=True)
        return True
    except:
        return False
