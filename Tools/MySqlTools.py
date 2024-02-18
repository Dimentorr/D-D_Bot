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
                    print('MySQL Tools, result:', result)
                    connection.commit()
                    return result
        except mysql.connector.Error as e:
            err_text = f'MySQL Tools, err: {e}'
            print(err_text)
            connection.rollback()
            return 0
