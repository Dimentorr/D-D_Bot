import mysql.connector
from Tools.JsonTools import CatalogJson


def create_table():
    env = CatalogJson(name='file/json/environment.json')

    try:
        with mysql.connector.connect(
                host=env.read_json_data('DB_host'),
                port=env.read_json_data('DB_port'),
                database=env.read_json_data('DB_database'),
                user=env.read_json_data('DB_user'),
                password=env.read_json_data('DB_password')
        ) as connection:
            # user_id, name_character, webViewLink, file_id
            query_main_info_character = (f'CREATE TABLE IF NOT EXISTS characters_list('
                                         f'id int not null primary key auto_increment,'
                                         f'user_id int not null,'
                                         f'name_character varchar(255) not null,'
                                         f'link varchar(512) not null,'
                                         f'file_id varchar(512) not null'
                                         f');')
            # query_main_info_character = (f'CREATE TABLE IF NOT EXISTS characters_list('
            #                              f')')
            # print(query_main_info_character)
            # (f'CREATE TABLE IF NOT EXISTS verify('
            #  f'id int not null primary key auto_increment,'
            #  f'gmail int not null,'
            #  f'user_id int not null'
            #  f')')
            query_foreign_key_characters_list = (
                f'ALTER TABLE characters_list'
                f' ADD FOREIGN KEY (user_id) REFERENCES users(id)'
                f' ON DELETE RESTRICT ON UPDATE RESTRICT;')
            with connection.cursor() as cursor:
                cursor.execute(query_main_info_character)
                # result = cursor.fetchall()
                # print('MySQL Tools, result:', result)
                # указываем user_id как внешний ключ с таблицей users
                cursor.execute(query_foreign_key_characters_list)
                connection.commit()
                # пример добавления персонажа(в таблице временно отсутствует большая часть данных)
                # INSERT
                # INTO
                # `characters_list`(`id`, `user_id`, `name_character`)
                # VALUES('1', '1', 'Чармондер');
                # return result
    except mysql.connector.Error as e:
        err_text = f'MySQL Tools, err: {e}'
        print(err_text)
        return 0
