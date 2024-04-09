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
                query_main_info_character = (f'CREATE TABLE IF NOT EXISTS characters_list('
                                             f'id int not null primary key auto_increment,'
                                             f'user_id int not null,'
                                             f'name_character varchar(255) not null,'
                                             f'link varchar(512) not null,'
                                             f'file_id varchar(512) not null'
                                             f');')
                query_foreign_key_characters_list = (
                    f'ALTER TABLE characters_list '
                    f'ADD FOREIGN KEY (user_id) REFERENCES users(id) '
                    f'ON DELETE RESTRICT ON UPDATE RESTRICT;')
                with connection.cursor() as cursor:
                    cursor.execute(query_main_info_character)
                    # указываем user_id как внешний ключ с таблицей users
                    cursor.execute(query_foreign_key_characters_list)
                    connection.commit()
        except mysql.connector.Error as e:
            err_text = f'MySQL Tools, err: {e}'
            print(err_text)
            return 0
    else:
        con = Connection(path=os.getenv('path_sqlite_db'))
        try:
            con.work_with_SQLite(query=[f'CREATE TABLE IF NOT EXISTS characters_list('
                                        f'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                                        f'user_id int not null,'
                                        f'name_character varchar(255) not null,'
                                        f'link varchar(512) not null,'
                                        f'file_id varchar(512) not null,'
                                        f'FOREIGN KEY (user_id) REFERENCES users(id) '
                                        f'ON DELETE RESTRICT ON UPDATE RESTRICT'
                                        f');'])
        except Exception as e:
            err_text = f'SQLite Tools, err: {e}'
            print(err_text)
            return 0

