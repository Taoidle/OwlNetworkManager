from config import DB_PATH as db_path
import sqlite3
import os


class Sqlite:
    _instance = None
    conn, cursor = None, None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            print("path: ", db_path)
            if os.path.exists(db_path):
                cls.conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                           isolation_level=None)
                cls.cursor = cls.conn.cursor()
                if cls.cursor.execute('''SELECT count(*) FROM sqlite_master WHERE type="table" AND name = "OFFLINE"''').fetchall()[0][0] == 0:
                    cls.cursor.execute('''CREATE TABLE OFFLINE
                                                       (ID INT PRIMARY KEY     NOT NULL,
                                                       NAME           TEXT    NOT NULL,
                                                       ADDRESS        TEXT    NOT NULL,
                                                       MAIN           TEXT    NOT NULL);''')
                if cls.cursor.execute('''SELECT count(*) FROM sqlite_master WHERE type="table" AND name = "ENV"''').fetchall()[0][0] == 0:
                    cls.cursor.execute('''CREATE TABLE ENV
                                                       (PACKAGE TEXT PRIMARY KEY,
                                                       VERSION    TEXT,
                                                       TAG        TEXT);''')
            else:
                cls.conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                           isolation_level=None)
                cls.cursor = cls.conn.cursor()
                cls.conn.execute('PRAGMA encoding="UTF-8"')
                cls.cursor.execute('''CREATE TABLE OFFLINE
                                   (ID INT PRIMARY KEY     NOT NULL,
                                   NAME           TEXT    NOT NULL,
                                   ADDRESS        TEXT    NOT NULL,
                                   MAIN           TEXT    NOT NULL);''')
                cls.cursor.execute('''CREATE TABLE ENV
                                   (PACKAGE TEXT PRIMARY KEY,
                                   VERSION    TEXT,
                                   TAG        TEXT);''')
                cls.conn.commit()
        return cls._instance

    def __int__(self):
        pass

    async def close(self):
        self.cursor.close()
        self.conn.close()
