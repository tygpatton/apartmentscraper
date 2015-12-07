import requests
from bs4 import BeautifulSoup


class ScrapeAptListings(object):

	def __init__(self, city):
		self.city = city
		self.url = 'http://' + city + '.craigslist.org/search/apa?'

	
	def ScrapeMain(self, min_rent=None, max_rent=None,
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

		raw_html = requests.get(self.url)
		#print raw_html.content

		soup = BeautifulSoup(raw_html.content, 'html.parser')

		
		rows = soup.select('.row')
		data_list = []

		for row in rows:
			data_dict = {}
			data_dict['c_id'] = row['data-pid']
			data_dict['price'] = row.select('.price')[0].text
			data_dict['nhood']  = row.select('.pnr > small')[0].text
			data_dict['tmstmp'] = row.select('.pl > time')[0]['datetime']
			data_dict['title'] = row.select('.hdrlnk')[0].text
			


	def IterateListings(self, listing_urls):

		base_url = 'http://' + self.city + 'craigslist.org'

		for listing in listing_urls:

			
			


	def CheckIfSearchTerm(self):	
		pass	