import mysql.connector
from Tools.SQLiteTools import Connection

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')


def create_table(is_mysql=True):
    if is_mysql:
        try:
            with mysql.connector.connect(
                    host=os.getenv('DB_host'),
                    port=os.getenv('DB_port'),
                    database=os.getenv('DB_database'),
                    user=os.getenv('DB_user'),
                    password=os.getenv('DB_password')
            ) as connection:
                query = (f'CREATE TABLE IF NOT EXISTS users('
                         f'id int not null primary key auto_increment,'
                         f'user_id varchar(255) not null,'
                         f'name_user varchar(255) not null,'
                         f'password varchar(255) not null,'
                         f'is_login int not null default(1)'
                         f')')
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    connection.commit()
                    return result
        except mysql.connector.Error as e:
            err_text = f'MySQL Tools, err: {e}'
            print(err_text)
            return 0
    else:
        con = Connection(path=os.getenv('path_sqlite_db'))
        try:
            con.work_with_SQLite(query=[f'CREATE TABLE IF NOT EXISTS users('
                                        f'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                                        f'user_id varchar(255) not null,'
                                        f'name_user varchar(255) not null,'
                                        f'password varchar(255) not null,'
                                        f'is_login int not null default(1)'
                                        f')'])
        except Exception as e:
            err_text = f'SQLite Tools, err: {e}'
            print(err_text)
            return 0
