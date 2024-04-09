import mysql.connector
from Tools.SQLiteTools import Connection

import os
from dotenv import load_dotenv

load_dotenv()


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
                query_verify = (f'CREATE TABLE IF NOT EXISTS verify('
                                f'id int not null primary key auto_increment,'
                                f'gmail varchar(255) not null,'
                                f'user_id int not null'
                                f')')
                query_verify_foreign_key = (
                    f'ALTER TABLE verify '
                    f'ADD FOREIGN KEY (user_id) REFERENCES users(id) '
                    f'ON DELETE RESTRICT ON UPDATE RESTRICT;')
                with connection.cursor() as cursor:
                    cursor.execute(query_verify)
                    cursor.execute(query_verify_foreign_key)
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
            con.work_with_SQLite(query=[f'CREATE TABLE IF NOT EXISTS verify('
                                        f'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                                        f'gmail varchar(255) not null,'
                                        f'user_id int not null,'
                                        f'FOREIGN KEY (user_id) REFERENCES users(id) '
                                        f'ON DELETE RESTRICT ON UPDATE RESTRICT'
                                        f')'])
        except Exception as e:
            err_text = f'SQLite Tools, err: {e}'
            print(err_text)
            return 0
