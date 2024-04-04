import mysql.connector


class Connection:
    def __init__(self, host: str, port: str,
                 database_name: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password

    def main_query_block(self, connection, query_text):
        query = query_text
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        try:
            connection.commit()
        except Exception as err:
            print(f'Невозможно сохранить изменения')
            print(f'Ошибка - {err}')
        return result

    def work_with_MySQL(self, query_text=list):
        try:
            with mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database_name,
                    user=self.user,
                    password=self.password
            ) as connection:
                for i in query_text:
                    if type(i) == str:
                        result = self.main_query_block(connection, i)
                    else:
                        for j in i:
                            result = self.main_query_block(connection, j)
                return result
        except mysql.connector.Error as e:
            print(f'(ERROR)MySQL Tools: {e}')
            connection.rollback()
            return 0

    def work_with_temporary_on_MySQL(self, query_text=list):
        try:
            with mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database_name,
                    user=self.user,
                    password=self.password
            ) as connection:
                for i in query_text:
                    if type(i) == str:
                        result = self.main_query_block(connection, i)
                    if type(i) == tuple:
                        # почему-то возникает баг, при котором в каскаде запросов с созданием временной таблицы
                        # функция вызывается ещё раз, но в качестве аргумента на вход подаётся уже полученный ответ
                        return query_text
                    else:
                        for j in i:
                            result = self.main_query_block(connection, j)
                return result
        except mysql.connector.Error as e:
            print(f'(ERROR)MySQL Tools: {e}')
            connection.rollback()
            return 0
