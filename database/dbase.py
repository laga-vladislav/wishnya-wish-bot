import psycopg2
from psycopg2.extras import DictCursor

from settings import config

db_name = config.PSQL_DB_NAME
user = config.PSQL_DB_USER
password = config.PSQL_DB_PASSWORD
host = config.PSQL_DB_HOST


def select_call(call):
    if call[-1] != ';':
        call += ';'
    conn = psycopg2.connect(dbname=db_name, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(call)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records


def insert_call(call):
    if call[-1] != ';':
        call += ';'
    conn = psycopg2.connect(dbname=db_name, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(call)
    conn.commit()
    cursor.close()
    conn.close()


def update_call(call, values):
    if call[-1] != ';':
        call += ';'
    conn = psycopg2.connect(dbname=db_name, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(call, values)
    conn.commit()
    cursor.close()
    conn.close()


def delete_call(call):
    conn = psycopg2.connect(dbname=db_name, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(call)
    conn.commit()
    cursor.close()
    conn.close()
