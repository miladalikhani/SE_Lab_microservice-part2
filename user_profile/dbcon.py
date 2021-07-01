import sqlite3
from flask import g

DATABASE = 'user_profile.db'


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
    create table if not exists user_profile
    (
        id integer primary key,
        username text not null,
        first_name text not null,
        last_name text not null
    );
    """)


def get_all_profiles():
    users_profile = query_db("""
    select username, first_name, last_name from user_profile;
    """)
    return users_profile


def get_user_profile(username):
    if profile_exists(username):
        user_profile = query_db("""
        select username, first_name, last_name from user_profile
        where username like ?
        """, [username], one=True)
        return True, user_profile
    return False, {}


def profile_exists(username):
    profiles = get_all_profiles()
    for entity in profiles:
        if entity['username'] == username:
            return True
    return False


def write_new_profile(username, first_name, last_name):
    try:
        query_db("""
        insert into user_profile (username, first_name, last_name)
        values ( ? , ? , ? )
        """, [username, first_name, last_name], commit=True)
        return True
    except:
        return False


def update_profile(username, first_name, last_name):
    try:
        query_db("""
        update user_profile set first_name = ? , last_name = ?
        where username like ?
        """, [first_name, last_name, username], commit=True)
        return True
    except:
        return False
