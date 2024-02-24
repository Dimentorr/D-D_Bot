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
            query_stories = (f'CREATE TABLE IF NOT EXISTS game_stories('
                             f'id int not null primary key auto_increment,'
                             f'GM_id int not null,'
                             f'name_story varchar(255) not null,'
                             f'password varchar(255) not null,'
                             f'id_group varchar(255) not null'
                             f')')
            query_player_story = (f'CREATE TABLE IF NOT EXISTS players_stories('
                                  f'id int not null primary key auto_increment,'
                                  f'player_id int not null,'
                                  f'story_id int not null'
                                  f')')
            query_stories_foreign_key = (
                f'ALTER TABLE game_stories'
                f' ADD FOREIGN KEY (GM_id) REFERENCES users(id)'
                f' ON DELETE RESTRICT ON UPDATE RESTRICT;')
            query_player_players_story_foreign_key = (
                f'ALTER TABLE players_stories'
                f' ADD FOREIGN KEY (player_id) REFERENCES users(id)'
                f' ON DELETE RESTRICT ON UPDATE RESTRICT;')
            query_story_players_story_foreign_key = (
                f'ALTER TABLE players_stories'
                f' ADD FOREIGN KEY (story_id) REFERENCES game_stories(id)'
                f' ON DELETE RESTRICT ON UPDATE RESTRICT;')
            with connection.cursor() as cursor:
                cursor.execute(query_stories)
                cursor.execute(query_player_story)
                cursor.execute(query_stories_foreign_key)
                cursor.execute(query_player_players_story_foreign_key)
                cursor.execute(query_story_players_story_foreign_key)
                result = cursor.fetchall()
                print('MySQL Tools, result:', result)
                connection.commit()
                return result
    except mysql.connector.Error as e:
        err_text = f'MySQL Tools, err: {e}'
        print(err_text)
        return 0
