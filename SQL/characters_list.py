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
            query_main_info_character = (f'CREATE TABLE IF NOT EXISTS characters_list('
                                         f'id int not null primary key auto_increment,'
                                         f'user_id int not null,'
                                         f'name_character varchar(255) not null,'
                                         f'class varchar(255) not null,'
                                         f'story varchar(255),'
                                         f'worldview varchar(255),'
                                         f'XP int default(0) not null,'
                                         f'level int default(1) not null,'
                                         f'saving_throws_success int default(0) not null,'
                                         f'saving_throws_failure int default(0) not null,'
                                         f'attributes_strong int not null,'
                                         f'attributes_sleight int not null,'
                                         f'attributes_body int not null,'
                                         f'attributes_intelligence int not null,'
                                         f'attributes_wisdom int not null,'
                                         f'attributes_charisma int not null,'
                                         f'dice_for_HP_count int default(1) not null,'
                                         f'dice_for_HP_dice varchar(255) not null,'
                                         f'personal_traits_character_traits varchar(255),'
                                         f'personal_traits_ideals varchar(255),'
                                         f'personal_traits_attachments varchar(255),'
                                         f'personal_traits_weaknesses varchar(255),'
                                         f'possessions varchar(255) not null,'
                                         f'abilities varchar(255) not null,'
                                         f'defence int not null,'
                                         f'initiative int not null,'
                                         f'speed int not null,'
                                         f'maxHP int not null,'
                                         f'minHP int not null,'
                                         f'skills varchar(255) not null,'
                                         f'saving_throws_attributes varchar(255) not null,'
                                         f'inventory_cash varchar(255),'
                                         f'inventory_bag varchar(255)'
                                         f');')
            query_magic_part = (f'CREATE TABLE IF NOT EXISTS characters_magic_list('
                                f'id int not null primary key auto_increment,'
                                f'character_id int not null,'
                                f'name_character varchar(255),'
                                f'class varchar(255),'
                                f'main_attribute varchar(255),'
                                f'difficult_saving_throws int,'
                                f'bonus_attack int,'
                                f'zero_count_all int,'
                                f'zero_battle_count int,'
                                f'zero_spells varchar(255),'
                                f'one_count_all int,'
                                f'one_battle_count int,'
                                f'one_spells varchar(255),'
                                f'two_count_all int,'
                                f'two_battle_count int,'
                                f'two_spells varchar(255),'
                                f'three_count_all int,'
                                f'three_battle_count int,'
                                f'three_spells varchar(255),'
                                f'four_count_all int,'
                                f'four_battle_count int,'
                                f'four_spells varchar(255),'
                                f'five_count_all int,'
                                f'five_battle_count int,'
                                f'five_spells varchar(255),'
                                f'six_count_all int,'
                                f'six_battle_count int,'
                                f'six_spells varchar(255),'
                                f'seven_count_all int,'
                                f'seven_battle_count int,'
                                f'seven_spells varchar(255),'
                                f'eight_count_all int,'
                                f'eight_battle_count int,'
                                f'eight_spells varchar(255),'
                                f'nine_count_all int,'
                                f'nine_battle_count int,'
                                f'nine_spells varchar(255)'
                                f');')
            query_foreign_key_characters_list = (
                f'ALTER TABLE characters_list'
                f' ADD FOREIGN KEY (user_id) REFERENCES users(id)'
                f' ON DELETE RESTRICT ON UPDATE RESTRICT;')
            query_foreign_key_characters_magic_list = (
                f'ALTER TABLE characters_magic_list'
                f' ADD FOREIGN KEY (character_id) REFERENCES characters_list(id)'
                f' ON DELETE RESTRICT ON UPDATE RESTRICT;')
            with connection.cursor() as cursor:
                cursor.execute(query_main_info_character)
                cursor.execute(query_magic_part)
                # result = cursor.fetchall()
                # print('MySQL Tools, result:', result)
                # указываем user_id как внешний ключ с таблицей users
                cursor.execute(query_foreign_key_characters_list)
                cursor.execute(query_foreign_key_characters_magic_list)
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
