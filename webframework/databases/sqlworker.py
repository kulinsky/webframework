from contextlib import closing
from abc import ABC, abstractmethod


class SQLWorker(ABC):
    @abstractmethod
    def create(self):
        raise NotImplementedError('users must define create')

    @abstractmethod
    def read(self):
        raise NotImplementedError('users must define read')

    @abstractmethod
    def update(self):
        raise NotImplementedError('users must define update')

    @abstractmethod
    def delete(self):
        raise NotImplementedError('users must define delete')


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

    def create(self, query, params={}):
        pass

    def read(self, query):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        return data

    def update(self, query, params={}):
        pass

    def delete(self, query, id):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, (id,))
                self.conn.commit()
        except sqlite3.IntegrityError:
            print("couldn't delet ", id)

# try:
#     with con:
#         con.execute("insert into person(firstname) values (?)", ("Joe",))
# except sqlite3.IntegrityError:
#     print "couldn't add Joe twice"

    def close(self):
        self.conn.close()
