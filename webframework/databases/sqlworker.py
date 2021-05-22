from contextlib import closing
from abc import ABC, abstractmethod


class SQLWorker(ABC):
    @abstractmethod
    def sql(self):
        """ return tuple(rowcount, list of tuples of values)
        ex.: (2, [('user1','city1'),('user2','city2')] )
        """
        pass


class SQLiteWorker(SQLWorker):
    def __init__(self, filename='sqlite.db'):
        import sqlite3
        self.conn = sqlite3.connect(filename)

    def sql(self, query, params=None):
        params = params or {}
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                return cursor.rowcount, cursor.fetchall()
        except sqlite3.IntegrityError as e:
            print(e)
        return None
