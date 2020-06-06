"""
Changelog/ notes log

Jackson, June 6, 2020
- I didn't test this at all
- Used foster's presumably working code
- PLEASE TEST BEFORE MERGING TO MASTER
"""

import googlemaps
import os
from DBManager import *

class LocationManager:
	def __init__(self, api_key=None):
		self.api_key = api_key

		if api_key is None:
			self.gmaps = googlemaps.Client(key=os.environ.get('API_KEY'))
		else:
			self.gmaps = googlemaps.Client(key=self.api)

	def add_location_data(self, db_manager):
		"""
			Goes through db_manager's db and adds location_data to all that it can

			Note to dev team: I haven't tested this yet bc i don't have api key.
		"""

		count = 0
		next_up = db_manager.get_next_empty_loc()
		while next_up is not None:
			coords = dict()
			code_res = self.gmaps.geocode(location)
			print('Location results:', len(code_res))
			coords = code_res[0]['geometry']['location']

			lat, lon = coords['lat'], coords['lng']

			db_manager.update_location(next_up[0], lat, lon)
			next_up = db_manager.get_next_empty_loc()

			count += 1

		print(f"Generated locations for {count} POI")
		return True



		