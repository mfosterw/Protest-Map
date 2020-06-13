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
import datetime

class ProtestChicagoParser:
	def __init__(self, db_file="temp.db", db_manager=None):
		self.url = "https://www.protestchicago.com/"
		self.db_file = db_file

		if db_manager is None:
			self.db_manager = DBManager(self.db_file)
		else:
			self.db_manager = db_manager

	def process_time(self, time_str):
		months = {'January':1, 'February':2, 'March':3, 'April':4,
				'May':5, 'June':6, 'July':7, 'August':8, 'September':9,
				'October':10, 'November':11, 'December':12}
		numbers = "1234567890"
		# time formats
		# June 7, 2020 - 4:30 PM – 5:30 PM
		# June 7, 2020 - 10 AM
		# Month, day, year 'character' time
		ts = time_str.replace(",", "")
		ts = ts.split(" ")

		# first parse the month
		month = int(months[ts[0]])
		day = int(ts[1])
		year = int(ts[2])

		rest = "".join(ts[4:])

		h_flag, m_flag = True, False
		hour, minute = "0", "0"
		day_part = ""

		for char in rest:
			if char in numbers:
				if h_flag:
					hour += char
				elif m_flag:
					minute += char
				continue
			elif char == ":":
				if h_flag:
					h_flag, m_flag = False, True
			elif char.upper() == "A":
				day_part = "AM"
				break
			#The people who run protestchicago.com are kinda lazy tbh
			#Just gonna assume that if they don't specify then it's PM
			elif char.upper() == "P" or char in '-–':
				day_part = "PM"
				break
			else:
				print("Wack time!", char)
				print(''.join(time_str))
		hour, minute = int(hour), int(minute)
		if day_part == "PM" and hour < 12:
			hour += 12

		# print(ts, f"{month} {day}, {year}, h={hour} m={minute} ")

		epoch = datetime.datetime(1970,1,1)
		new_time = datetime.datetime(year,month, day, hour=hour, minute=minute)
		seconds_from_epoch = (new_time-epoch).total_seconds()

		return (seconds_from_epoch, new_time.strftime('%A, %B %d %Y at %I:%M %p'))


	#ALL PARSERS SHOULD HAVE A .parse() that does the parsing, and saves to the DB. Can or cannot have lat long implementation
	def parse(self):
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

					locstr = article.find('h3').get_text(separator="\n")
					locations = locstr.split("\n")
					location = locations[0]
					if location and 'Chicago'.lower() not in location.lower():
						location += ', Chicago'
					print(location)

					# isolate the link from the h1 a tag
					found_url = title_h1.find(href=True)['href']

					# notes are probably in the p-tag
					notes = article.find('p').get_text()

					(time_seconds, time_info) = self.process_time(time_info)

					if not self.db_manager.check_val_in(str(found_url), "url"): # If the value isn't in the field already
						added_count += 1

						protest = (title, time_info, location, 0.0, 0.0, found_url, notes, time_seconds)
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
