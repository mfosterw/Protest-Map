"""
Changelog/ notes log

Jackson, June 5, 2020
 - Initial commit by Jackson
 - Please follow the conventions, it'll make stuff easier in the future!

Jackson, June 6, 2020
 - Don't have API key so can't test the adding location data
 - hopefully will work
"""

from DBManager import *
from ProtestChicagoParser import *
from LocationManager import *

class MainProtestFinder:
	def __init__(self, db_name):
		self.db = DBManager(db_name)
		self.parsers = [ProtestChicagoParser(db_manager=self.db)]


	def do_parses(self):
		for parser in self.parsers:
			parser.parse()

	def export_json(self, path, geopath='files/geoprotest.json', save_old=False):
		self.db.save_json(path, save_old)
		self.db.save_geojson(geopath, save_old)

	def get_dbm(self):
		return self.db

if __name__ == "__main__":
	locM = LocationManager(os.environ.get('API_KEY'))

	mpf = MainProtestFinder("files/protests.db")
	mpf.do_parses()

	locM.add_location_data(mpf.get_dbm())

	mpf.export_json("files/protestjson.json", "files/geoprotest.json", False)
