import urllib2, urllib, re, time
from BeautifulSoup import BeautifulSoup

from scrapers.general import Scraper

class FlatpageScraper(Scraper):
  def __init__(self, *args, **kwargs):
    super(FlatpageScraper, self).__init__(*args, **kwargs)
    self.urls = []
  
  def run(self):
    self.get_all_urls()
    for url in self.urls:
      self._process_url(url)
  
  def _process_url(self, url):
    soup = BeautifulSoup(urllib2.urlopen(url))
    self.parse_url(url, soup)