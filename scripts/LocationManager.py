"""
Changelog/ notes log

Jackson, June 6, 2020
- I didn't test this at all
- Used foster's presumably working code
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
			self.gmaps = googlemaps.Client(key=self.api_key)

	def add_location_data(self, db_manager, default=(41.8781, -87.6298)):
		"""
			Goes through db_manager's db and adds location_data to all that it can
		"""

		count = 0
		coords = dict()
		next_up = db_manager.get_next_empty_loc()
		while next_up is not None:
			location = next_up[1]
			if location:
				raise SystemExit('No spending money')
				code_res = self.gmaps.geocode(location)
				print('Location results:', len(code_res))
				coords = code_res[0]['geometry']['location']

				lat, lon = coords['lat'], coords['lng']
			else:
				lat, lon = default

			db_manager.update_location(next_up[0], lat, lon)
			next_up = db_manager.get_next_empty_loc()

			count += 1

		print(f"Generated locations for {count} POI")
		return True
