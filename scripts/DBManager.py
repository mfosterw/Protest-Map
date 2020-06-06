"""
Changelog/ notes log

Jackson, June 5, 2020
 - Initial commit by Jackson
 - Please follow the conventions, it'll make stuff easier in the future!
 - Recommend to only use one instance of DBManager, and to pass it by reference to the various parsers.
 - See 'ProtestChicagoParser' for how to effectively do so

 Jackson, June 6, 2020
 - Added functions and comments for easilly retrieving rows that need location data
 - Added functions and comments for easilly updating rows to include location data
 -
"""

import sqlite3
from sqlite3 import Error
import json

def dict_factory(cursor, row):
    # http://www.cdotson.com/2014/06/generating-json-documents-from-sqlite-databases-in-python/
    # just works. yay.
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBManager:
    def create_protest_table(self):
        create_protests = """CREATE TABLE IF NOT EXISTS protests (
                                id integer PRIMARY KEY,
                                title text NOT NULL,
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
        """
            Creates the database manager for the database at file path :database_file:
        """

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
        print("Successfully closed database connection")

    def create_protest(self, protest):
        """
        Create a new protest into the protests table
        :param protest:
        :return: project id

        protest takes (name, time_info, location, latitude, longitude, url, notes)
        """
        sql = '''INSERT INTO protests(title, time_info, location, latitude, longitude, url, notes)
                VALUES(?, ?, ?, ?, ?, ?, ?)'''
        try:
            cur = self.conn.cursor()
            cur.execute(sql, protest)
            return cur.lastrowid
        except Error as e:
            print(e)
            print("ERROR IN CREATE PROTEST", protest)
            return None

    def check_val_in(self, value, column):
        """
            Checks if value is in the given column of table protests

            Returns TRUE if it is; False if it is now
        """

        sql = f'''SELECT * FROM protests WHERE {column} = "{value}" '''

        cur = self.conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        return len(results) > 0

    def get_all_protests(self):
        """
            Returns a list of tuples of all of the db rows

            Useful for debugging
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM protests')

        return cursor.fetchall()

    """
        JSON Handling
    """

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
        """
            Saves data from Database into structured JSON file.
            Exxports to path json_path
        """
        with open(json_path, 'w+') as file:
            json_data = self.generate_json()
            file.seek(0)
            file.write(json.dumps(json_data))

            file.truncate()
        print(f"Successfully saved JSON file to {json_path}")

    def save_geojson(self, filepath):
        """Saves data in GeoJson format"""
        with open(filepath, 'w+') as file:
            raw_json = self.generate_json()
            geojson = {'type': 'FeatureCollection', 'features': []}
            for protest in raw_json:
                feature = {'type': 'Feature',
                           'properties': {k: v for k, v in protest.items()
                                          },
                           'geometry':
                                {'type': 'Point',
                                'coordinates': [float(protest['longitude']),
                                                float(protest['latitude'])]
                                        }
                           }
                geojson['features'].append(feature)

            file.seek(0)
            file.write(json.dumps(geojson))

            file.truncate()
        print(f'Saved GeoJson data to {filepath}')

    """
        Location managing and updating
    """

    def get_next_empty_loc(self):
        """
            Returns none if none remaining

            Returns (id, location) otherwise
        """
        flag = 0
        if self.conn is None:
            flag = 1
            self.create_connection()

        cursor = self.conn.cursor()
        cursor.execute("""SELECT id, location FROM protests WHERE latitude IS 0.0 AND longitude IS 0.0;""")

        results = cursor.fetchall()

        if flag:
            self.close_connection()

        if len(results) == 0:
            return None
        return results[0]

    def update_location(self, id_, latitude, longitude):
        """ Updates row id of protests, adding latitude and longitude
            Meant to be used in conjunction with get_next_empty_loc to fill in all needed lat long data
        """

        flag = 0
        if self.conn is None:
            flag = 1
            self.create_connection()
        sql = f"""UPDATE protests SET latitude = {latitude}, longitude = {longitude} WHERE id={id_}"""

        cursor = self.conn.cursor()
        cursor.execute(sql)

        if flag:
            self.close_connection()
