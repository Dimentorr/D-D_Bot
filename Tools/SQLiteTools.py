import sqlite3


class Connection:
    def __init__(self, path: str):
        self.path = path

    def main_query_block(self, db, query_text):
        cur = db.cursor()
        result = cur.execute(query_text).fetchall()
        try:
            db.commit()
        except Exception as err:
            print(f'Невозможно сохранить изменения')
            print(f'Ошибка - {err}')
        return result

    def work_with_SQLite(self, query: list):
        try:
            db = sqlite3.connect(self.path)
            for i in query:
                if type(i) == str:
                    result = self.main_query_block(db, i)
                else:
                    for j in i:
                        result = self.main_query_block(db, j)
            db.close()

            return result
        except Exception as err:
            print(f'Невозможно сохранить изменения')
            print(f'Ошибка - {err}')
        return []
