import mysql.connector
from Tools.SQLiteTools import Connection
from Tools.JsonTools import CatalogJson


def create_table(is_mysql=True):
    if is_mysql:
        env = CatalogJson(name='file/json/environment.json')

        try:
            with mysql.connector.connect(
                    host=env.read_json_data('DB_host'),
                    port=env.read_json_data('DB_port'),
                    database=env.read_json_data('DB_database'),
                    user=env.read_json_data('DB_user'),
                    password=env.read_json_data('DB_password')
            ) as connection:
                query_main_info_character = (f'CREATE TABLE IF NOT EXISTS selected_characters('
                                             f'id int not null primary key auto_increment,'
                                             f'story_id int not null,'
                                             f'character_id int not null,'
                                             f'player_id int not null'
                                             f');')
                query_foreign_key_character_id = (
                    f'ALTER TABLE selected_characters '
                    f'ADD FOREIGN KEY (character_id) REFERENCES characters_list(id) '
                    f'ON DELETE RESTRICT ON UPDATE RESTRICT;')
                query_foreign_key_story_id = (
                    f'ALTER TABLE selected_characters '
                    f'ADD FOREIGN KEY (story_id) REFERENCES game_stories(id) '
                    f'ON DELETE RESTRICT ON UPDATE RESTRICT;')
                query_foreign_key_player_id = (
                    f'ALTER TABLE selected_characters '
                    f'ADD FOREIGN KEY (player_id) REFERENCES users(id) '
                    f'ON DELETE RESTRICT ON UPDATE RESTRICT;')

                with connection.cursor() as cursor:
                    cursor.execute(query_main_info_character)
                    # указываем user_id как внешний ключ с таблицей users
                    cursor.execute(query_foreign_key_character_id)
                    cursor.execute(query_foreign_key_story_id)
                    cursor.execute(query_foreign_key_player_id)
                    connection.commit()
        except mysql.connector.Error as e:
            err_text = f'MySQL Tools, err: {e}'
            print(err_text)
            return 0
    else:
        con = Connection(path='file/db/bot_base.db')
        try:
            con.work_with_SQLite(query=[f'CREATE TABLE IF NOT EXISTS selected_characters('
                                        f'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
                                        f'story_id int not null,'
                                        f'character_id int not null,'
                                        f'player_id int not null,'
                                        f'FOREIGN KEY (story_id) REFERENCES game_stories(id) '
                                        f'ON DELETE RESTRICT ON UPDATE RESTRICT,'
                                        f'FOREIGN KEY (character_id) REFERENCES characters_list(id) '
                                        f'ON DELETE RESTRICT ON UPDATE RESTRICT,'
                                        f'FOREIGN KEY (player_id) REFERENCES users(id) '
                                        f'ON DELETE RESTRICT ON UPDATE RESTRICT'
                                        f');'])
        except Exception as e:
            err_text = f'SQLite Tools, err: {e}'
            print(err_text)
            return 0
