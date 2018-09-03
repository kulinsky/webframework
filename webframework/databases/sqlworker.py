import sqlite3


class SQLWorker:
    def create(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class SQLiteWorker(SQLWorker):
    def __init__(self, filename):
        pass
