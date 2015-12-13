import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import boto


db_client = MongoClient()
db = db_client['SF']
tab = db['test']


class ScrapeAptListings(object):

	def __init__(self, city):
		self.city = city
		self.url = 'http://' + city + '.craigslist.org/search/apa?'

	
	def ScrapeMain(self, min_rent=None, max_rent=None,
				bedrooms=None, bathrooms=None, min_sq_ft=None,
				max_sq_ft=None, start=0):


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

		for row in rows:
			data_dict = {}
			data_dict['c_id'] = row['data-pid']
			data_dict['tmstmp'] = row.select('.pl > time')[0]['datetime']
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
			

			try:
				tab.insert(data_dict)
			except:
				print "Error inserting listing %s" % row['data-pid']
				continue


	def IterateListings(self, url_list):
		base = 'http://craigslist.org'

		for url in url_list:
			d_dict = {}
			r = requests.get(base + url)

			if r.status_code != 200:
				print 'Error retrieving listing %s' % url
				print 'Status Code: ', r.status_code
				print
				continue

			soup = BeautifulSoup(r.content, 'html.parser')

			try:
				d_dict['latitude'] = soup.select('.mapbox > div')[0]['data-latitude']
				d_dict['longitude'] = soup.select('.mapbox > div')[0]['data-longitude']
			except:
				print 'No location info for listing %s' % url

			try:
				d_dict['size'] = list(soup.select('.attrgroup sup')[0].parent)[0].text
			except:
				print 'No size info for listing %s' % url

		
			try:
				d_dict['address'] = soup.select('.mapaddress')[0].text
			except:
				print 'No address for listing %s' % url

			try:
				tab.update_one({'web_url': url}, {'$set': d_dict})
			except:
				print "Unable to update listing %s" % url

