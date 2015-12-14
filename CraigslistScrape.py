import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import json
import datetime

# if using Mongo:
# db_client = MongoClient()
# db = db_client['SF']
# tab = db['test']


class ScrapeAptListings(object):

	def __init__(self, city, keep_running=True, max_date=None):
		self.city = city
		self.url = 'http://' + city + '.craigslist.org/search/apa?'
		self.keep_running = keep_running
		self.max_date = max_date
	
	def scrape(self, start=0, min_rent=None, max_rent=None,
				bedrooms=None, bathrooms=None, min_sq_ft=None,
				max_sq_ft=None):

		if min_rent:
			self.url += '&min_price=' + min_rent
		if max_rent:
			self.url += '&max_price=' + max_rent
		if bedrooms:
			self.url += '&bedrooms=' + bedrooms
		if bathrooms:
			self.url += '&bathrooms=' + bathrooms
		if min_sq_ft:
			self.url += '&minSqft==' + min_sq_ft
		if max_sq_ft:
			self.url += '&maxSqft==' + max_sq_ft

		self.url += 's=%s' % start

		raw_html = requests.get(self.url)
		#print raw_html.content

		soup = BeautifulSoup(raw_html.content, 'html.parser')
		
		rows = soup.select('.row')

		data_list = []

		for row in rows:
			data_dict = {}
			data_dict['c_id'] = row['data-pid']
			current_date = row.select('.pl > time')[0]['datetime']
			data_dict['tmstmp'] = current_date
			data_dict['title'] = row.select('.hdrlnk')[0].text
			data_dict['web_url'] = row.select('.hdrlnk')[0]['href']

			try:
				data_dict['price'] = row.select('.price')[0].text
			except:
				print "No price for listing %s" % row['data-pid']

			try:
				nhood  = row.select('.pnr > small')[0].text.strip(' ()')
				data_dict['nhood'] = nhood
			except:
				print "No neighborhood for listing %s" % row['data-pid']

			# date control features
			conv_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M')

			if not self.max_date:
				self.max_date = conv_date

			elif conv_date > self.max_date:
				self.max_date = conv_date
			
			else:
				self.write_max_date()
				self.keep_running = False
				break

			data_list.append(data_dict)
			# If inserting into Mongo:
			# try:
			# 	tab.insert(data_dict)
			# except:
			# 	print "Error inserting listing %s" % row['data-pid']
			# 	continue

		for listing in data_list:
			additional = self.scrape_listing(listing['web_url'])
			listing.update(additional)

		return data_list

	def scrape_listing(self, list_id):

		base = 'http://www.craigslist.org'
		d_dict = {}
		r = requests.get(base + list_id)

		if r.status_code != 200:
			print 'Error retrieving listing %s' % list_id
			print 'Status Code: ', r.status_code
			print

		soup = BeautifulSoup(r.content, 'html.parser')

		try:
			d_dict['latitude'] = soup.select('.mapbox > div')[0]['data-latitude']
			d_dict['longitude'] = soup.select('.mapbox > div')[0]['data-longitude']
		except:
			print 'No location info for listing %s' % list_id

		try:
			d_dict['size'] = list(soup.select('.attrgroup sup')[0].parent)[0].text
		except:
			print 'No size info for listing %s' % list_id

	
		try:
			d_dict['address'] = soup.select('.mapaddress')[0].text
		except:
			print 'No address for listing %s' % list_id

		# If inserting into Mongo:
		# try:
		# 	tab.update_one({'web_url': url}, {'$set': d_dict})
		# except:
		# 	print "Unable to update listing %s" % url

		return d_dict


	def controlled_scrape(self):
		# add line to read in max date from other file
		today = datetime.date.today()
		s = 0
		data = []
		while self.keep_running:
			data += self.scrape(start=s)
			start += 100
		return data

	def write_max_date(self):
		with open('max_date.txt', 'w') as f:
			f.write(str(self.max_date))

	def read_max_date(self):
		with open('max_date.txt', 'r') as f:
			temp_date = f.read()
			temp_date = datetime.datetime.strptime(max_date, '%Y-%m-%d %H:%M')
			self.max_date = temp_date

	def write_json(self):


if __name__ == '__main__':
	scraper = ScrapeAptListings('sfbay')
	data_list = scraper.scrape()

	with open('test.json', 'w') as f:
		json.dump(data_list, f)





