import sqlite3 as sq
import json

__all__ = ['DataBase']


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


def include_db(method):
    def wrapper(*args, **kwargs):
        con = sq.connect(args[0].path)
        cursor = con.cursor()
        kwargs['cursor'] = cursor

        res = method(*args, **kwargs)

        con.commit()
        con.close()
        return res
    return wrapper


@singleton
class DataBase:
    def __init__(self, path='users.db', table_name='users'):
        self.__path = path
        self.__table_name = table_name
        self.__create_table(table_name)

    @include_db
    def __create_table(self, table_name, cursor=None):
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                        user_id TEXT,
                        balance TEXT,
                        target TEXT,
                        operations TEXT
                        )""")

    @property
    def path(self):
        return self.__path

    @property
    def table_name(self):
        return self.__table_name

    @include_db
    def insert_db(self, user_id, balance, cursor=None):
        dt = json.dumps({'operations': []})
        cursor.execute(
            f"""INSERT INTO {self.__table_name} VALUES ('{user_id}', '{balance}', 'Не установлена', '{dt}')"""
        )

    @include_db
    def update_db(self, user_id, column, value, cursor=None):
        cursor.execute(
            f"""UPDATE {self.__table_name} SET {column} = '{value}' WHERE user_id == '{user_id}'"""
        )

    @include_db
    def select_db(self, user_id, column, cursor=None):
        cursor.execute(
            f"""SELECT {column} FROM {self.__table_name} WHERE user_id == '{user_id}'"""
        )

        res = cursor.fetchall()
        return res

    @include_db
    def select_everything_db(self, user_id, cursor=None):
        cursor.execute(
            f"""SELECT balance, target, operations FROM {self.__table_name} WHERE user_id == '{user_id}'"""
        )

        res = cursor.fetchall()
        return res

