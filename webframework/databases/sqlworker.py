import sqlite3


class SQLWorker:
    def create(self):
        raise NotImplementedError
    
    def read(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class SQLiteWorker(SQLWorker):
    def __init__(self, filename='sqlite.db'):
        self.conn = sqlite3.connect(filename)
# try:
#     with con:
#         con.execute("insert into person(firstname) values (?)", ("Joe",))
# except sqlite3.IntegrityError:
#     print "couldn't add Joe twice"

    def close(self):
        self.conn.close()
