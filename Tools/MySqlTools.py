import mysql.connector


class Connection:
    def __init__(self, host: str, port: str,
                 database_name: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password


    def work_with_MySQL(self, query_text='Select * from users'):
        try:
            with mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database_name,
                    user=self.user,
                    password=self.password
            ) as connection:
                query = (
                    query_text
                )
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    # print(f'---------------------------------------\n'
                    #       f'MySQL Tools, result: {result}\n'
                    #       f'{query_text}\n'
                    #       f'---------------------------------------')
                    connection.commit()
                    return result
        except mysql.connector.Error as e:
            err_text = f'(ERROR)MySQL Tools: {e}'
            print(err_text)
            print(query_text)
            connection.rollback()
            return 0
