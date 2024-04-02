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
