"""
Changelog/ notes log

Jackson, June 5, 2020
- Ok full disclosure: this uses no natural language processing, and is so hard coded
that if they change nearly any of their HTML tags this could break. With that said,
however, as of June 4 2020 file is working
"""

from DBManager import *
from bs4 import BeautifulSoup
import requests
import os

import googlemaps

class ProtestChicagoParser:
	def __init__(self, db_file="temp.db", db_manager=None):
		self.url = "https://www.protestchicago.com/"
		self.db_file = db_file

		if db_manager is None:
			self.db_manager = DBManager(self.db_file)
		else:
			self.db_manager = db_manager

		self.gmaps = googlemaps.Client(key=os.environ.get('API_KEY'))

	#ALL PARSERS SHOULD HAVE A .parse() that does the parsing, and saves to the DB. Can or cannot have lat long implementation
	def parse(self, geocode=False):
		# parse does the stiring of the beautiful soup to find the needed info
		# this is probably going to break near instantly, so beware!

        # protest takes (name, time_info, location, latitude, longitude, url, notes)
		self.db_manager.create_connection()

		found_count, added_count = 0, 0

		url = self.url

		try:
		# Paginate through each page of the site, using url as a flag
			while url is not None:
				headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36, accept-language: en-US,en'}

				# while url not None:
				page = requests.get(url=url, headers=headers)
				soup = BeautifulSoup(page.text, 'html.parser')
				articles = soup.find_all('article')

				for article in articles:
					found_count += 1

					# Isolate the h1 tag, extract title
					title_h1 = article.find('h1')
					title = title_h1.get_text()

					time_info = article.find('h2').get_text()

					location = article.find('h3').get_text()
					location = location.split("\n")
					location = location[0]

					# isolate the link from the h1 a tag
					found_url = title_h1.find(href=True)['href']

					# notes are probably in the p-tag
					notes = article.find('p').get_text()

					if not self.db_manager.check_val_in(str(found_url), "url"): # If the value isn't in the field already
						added_count += 1

						coords = dict()
						if geocode and location:
							code_res = self.gmaps.geocode(location)
							print('Location results:', len(code_res))
							coords = code_res[0]['geometry']['location']
						else:
							coords['lat'] = 0.0
							coords['lng'] = 0.0

						protest = (title, time_info, location, coords['lat'], coords['lng'], found_url, notes)
						self.db_manager.create_protest(protest)
					else:
						continue
						# print("skip")

				# Pagination code; search for a tag containing next page number
				# a tag with class "next page-numbers" is only generated when on a non-final page
				next_page = soup.find_all('a', class_="next page-numbers")
				if len(next_page) > 0:
					url = next_page[0]['href']
					print(f"Next page!!! Going to {url}")
				else:
					url = None

			self.db_manager.close_connection()
			return (found_count, added_count)

		except Error as e:
			print("ERROR IN ProtestChicagoParser/parse")
			raise

if __name__ == "__main__":
	pc = ProtestChicagoParser("files/protests.db")
	a = pc.parse()
	print(f"Located {a[0]} potential protests, added {a[1]} on Protest Chicago")
