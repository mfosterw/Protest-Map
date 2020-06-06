"""
Changelog/ notes log

Jackson, June 5, 2020
 - Initial commit by Jackson
 - Please follow the conventions, it'll make stuff easier in the future!

"""

from DBManager import *
from ProtestChicagoParser import *

class MainProtestFinder:
	def __init__(self, db_name):
		self.db = DBManager(db_name)
		self.parsers = [ProtestChicagoParser(db_manager=self.db)]

	def do_parses(self, geocode=False):
		for parser in self.parsers:
			parser.parse(geocode)

	def export_json(self, path, geopath='files/geoprotest.json'):
		self.db.save_json(path)
		self.db.save_geojson(geopath)

if __name__ == "__main__":
	mpf = MainProtestFinder("files/protests.db")
	mpf.do_parses(True)
	mpf.export_json("files/protestjson.json")
