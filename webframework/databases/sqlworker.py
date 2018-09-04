from contextlib import closing
from abc import ABC, abstractmethod


class SQLWorker(ABC):
    @abstractmethod
    def sql(self):
        raise NotImplementedError('users must define create')


class SQLiteWorker(SQLWorker):
    def __init__(self, filename='sqlite.db'):
        import sqlite3
        self.conn = sqlite3.connect(filename)

    def sql(self, query, params={}):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                return cursor.fetchall()
        except sqlite3.IntegrityError:
            print("Error with ", query)
        return None

    def close(self):
        self.conn.close()
