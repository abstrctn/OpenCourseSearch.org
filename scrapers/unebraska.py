import cookielib, urllib2, urllib, BeautifulSoup, re, time, pickle, json
from scrapers.general import Scraper
from scrapers.peoplesoft import PeopleSoftScraper, PeopleSoftScraperV2
from scrapers.loader import Loader
from courses.models import *
from pprint import pprint
import time

class UNebraskaScraper(PeopleSoftScraperV2):
  def __init__(self, *args, **kwargs):
    super(UNebraskaScraper, self).__init__(*args, **kwargs)
    
    self.params.update({
      'CLASS_SRCH_WRK2_INSTITUTION$47$': self.institution_code,
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY': 'N',
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY$chk': 'N',
      'CLASS_SRCH_WRK2_STRM$50$': self.term,
    })
    self.temp = 'https://myred.nebraska.edu/psp/myred/NBL/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL'
    self.home_url = 'https://csprdnu.nebraska.edu/psc/csprdnu/NBL/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?PortalActualURL=https%3a%2f%2fcsprdnu.nebraska.edu%2fpsc%2fcsprdnu%2fNBL%2fHRMS%2fc%2fCOMMUNITY_ACCESS.CLASS_SEARCH.GBL&PortalContentURL=https%3a%2f%2fcsprdnu.nebraska.edu%2fpsc%2fcsprdnu%2fNBL%2fHRMS%2fc%2fCOMMUNITY_ACCESS.CLASS_SEARCH.GBL&PortalContentProvider=HRMS&PortalCRefLabel=Class%20Search&PortalRegistryName=NBL&PortalServletURI=https%3a%2f%2fmyred.nebraska.edu%2fpsp%2fmyred%2f&PortalURI=https%3a%2f%2fmyred.nebraska.edu%2fpsc%2fmyred%2f&PortalHostNode=ENTP&NoCrumbs=yes&PortalKeyStruct=yes'
    self.scrape_url = 'https://csprdnu.nebraska.edu/psc/csprdnu/NBL/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL'
    self.ICFieldScroll = '104'
    
    self.timers = {'default': datetime.datetime.now()}
  
  def run(self, forever=False):
    self._click(self.temp) # touch home
    self._click(self.home_url) # touch home
    self.set_term()
    self.process_subjects()
  
  def set_term(self):
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_INSTITUTION$47$',
      'CLASS_SRCH_WRK2_INSTITUTION$47$': self.institution_code
    })
    self._click(self.scrape_url, self.params)
    self.parse_subjects(self._soup)
    
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_STRM$50$',
      'CLASS_SRCH_WRK2_STRM$50$': self.term,
      'CLASS_SRCH_WRK2_INSTITUTION$47$': self.institution_code
    })
    self._click(self.scrape_url, self.params)
  
  def parse_subjects(self, soup):
    options = soup.find('select', {'id': 'CLASS_SRCH_WRK2_SUBJECT$63$'}).findAll('option')
    self.subjects = {}
    for option in options:
      if option['value']:
        self.subjects[option['value']] = {'name': option.renderContents(), 'college': ''}
  
  def process_subject(self, section_code):
    print "Processing %s" % section_code
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_SUBJECT$63$',
      'CLASS_SRCH_WRK2_SUBJECT$63$': section_code,
      'CLASS_SRCH_WRK2_STRM$50$': self.term,
      'CLASS_SRCH_WRK2_INSTITUTION$47$': self.institution_code
    })
    self._click(self.scrape_url, self.params)
    
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH',
      'CLASS_SRCH_WRK2_SUBJECT$63$': section_code,
      'CLASS_SRCH_WRK2_UNITS_MAXIMUM': '20',
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY$chk': 'N',
      'CLASS_SRCH_WRK2_STRM$50$': self.term,
      'CLASS_SRCH_WRK2_INSTITUTION$47$': self.institution_code,
    })
    self._click(self.scrape_url, self.params)
    
    self.params.update({'ICAction': '#ICSave'})
    self._click(self.scrape_url, self.params)
    
    super(UNebraskaScraper, self).process_subject()
