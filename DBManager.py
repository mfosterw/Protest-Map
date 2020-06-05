"""
    Reccommend to only use one instance of DBManager, and to pass it by reference to the various parsers. 
    See 'ProtestChicagoParser' for how to effectively do so 
"""

import sqlite3
from sqlite3 import Error
import json

def dict_factory(cursor, row):
    # http://www.cdotson.com/2014/06/generating-json-documents-from-sqlite-databases-in-python/
    # this just works.
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBManager:
    def create_protest_table(self):
        create_protests = """CREATE TABLE IF NOT EXISTS protests (
    id integer PRIMARY KEY,
    name text NOT NULL,
    time_info text NOT NULL,
    latitude text NOT NULL,
    longitude text NOT NULL,
    location text NOT NULL,
    url text NOT NULL,
    notes text NOT NULL
);
    """
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_protests)
        except Error as e:
            print(e)

    def __init__(self, database_file):
        self.database_file = database_file
        self.conn = None

        self.create_connection()
        self.create_protest_table()
        self.close_connection()



    def create_connection(self):
        """
        Create a new connectoion to the stored database
        """
        if self.conn is not None:
            print("Connection already established.")
            return
        try:
            self.conn = sqlite3.connect(self.database_file)
            print("Version =", sqlite3.version)
            print("Connection Successfully established")
        except Error as e:
            print("[ZIGGY STARLIGHT]")
            print(e)

        
    def close_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
        print("Successfully closed dataase connection")

    def create_protest(self, protest):
        """
        Create a new protest into the protests table
        :param protest:
        :return: project id

        protest takes (name, time_info, location, latitude, longitude, url, notes)
        """
        sql = '''INSERT INTO protests(name, time_info, location, latitude, longitude, url, notes)
                VALUES(?, ?, ?, ?, ?, ?, ?)'''
        try:
            cur = self.conn.cursor()
            cur.execute(sql, protest)
            return cur.lastrowid
        except Error as e:
            print(e)
            print("ERROR IN CREATE PROTEST", protest)
            return None

    def check_val_in(self, value, collumn):
        """
            Checks if value is in collumn collumn of table protests

            Returns TRUE if it is; False if it is now
        """

        sql = f'''SELECT * FROM protests WHERE {collumn} = "{value}" '''
        
        cur = self.conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        return len(results) > 0

    def get_all_protests(self):
        """
            Returns a 
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM protests')

        return cursor.fetchall()

    

    def generate_json(self):
        """
            Generates json for all of the rows in the db, returns json string
        """
        flag = 0
        if self.conn is None:
            flag = 1
            self.create_connection()

        self.conn.row_factory = dict_factory
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM protests')

        results = cursor.fetchall()

        if flag:
            self.close_connection()

        return results

    def save_json(self, json_path):
        with open(json_path, 'w+') as file:
            json_data = self.generate_json()
            file.seek(0)
            file.write(json.dumps(json_data))

            file.truncate()
        print(f"Successfully saved JSON file to {json_path}")

