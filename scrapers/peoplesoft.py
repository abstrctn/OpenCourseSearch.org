import cookielib, urllib2, urllib, re, time
from BeautifulSoup import BeautifulSoup, SoupStrainer
from scrapers.general import Scraper
from courses.helpers import *
from courses.models import *
from pprint import pprint
import time, json, datetime


class PeopleSoftScraper(Scraper):
  def __init__(self, *args, **kwargs):
    super(PeopleSoftScraper, self).__init__(*args, **kwargs)
    self.ICSID = ''
    self.sections = None
    self.section_data = {}
    self.classes = {}
    self.hold = None
    self.username = kwargs.get('username')#username
    self.password = kwargs.get('password')#password
    self.params = {
      'ICAction': '',
      'ICChanged': '-1',
      'ICElementNum': '0',
      'ICFocus': '',
      'ICResubmit': '0',
      'ICSID': '1',
      'ICSaveWarningFilter': '0',
      'ICStateNum': '1',
      'ICType': 'Panel',
      'ICXPos': '0',
      'ICYPos': '0',
    }
    self.term = self.session.system_code
    
    self.start_index = kwargs.get('start', 0)#start
    if kwargs.get('end'):#end:
      self.end_index = self.start_index + kwargs['end']
    else:
      self.end_index = None
    
    self.last_section = ''
    self.longs = []
    
    self.cj = cookielib.CookieJar()
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
    self.timers = {}
    
  def _time(self, key):
    self.timers[key] = self.timers.get(key, {'total': datetime.timedelta(0)})
    self.timers[key]['last'] = datetime.datetime.now()
  
  def _elapsed(self, key):
    if self.debug and self.timers.get(key):
      self.timers[key]['total'] += datetime.datetime.now() - self.timers[key]['last']
      print "%s\t%s\t%s"% (key, datetime.datetime.now() - self.timers[key]['last'], self.timers[key]['total'])
  
  def _click(self, url = None, params = {}, soupify = True):
    if not url:
      url = self.scrape_url
    
    data = urllib.urlencode(params)
    self._elapsed('other')
    self._time('open')
    r = self.opener.open(url, data)
    page = r.read()
    self._page = page
    self._elapsed('open')
    if soupify:
      self._time('soup')
      self._soup = BeautifulSoup(page)
      self._elapsed('soup')
    self._time('other')
    
    try:
      if soupify:
        self.params = {}
        for hidden in self._soup.findAll('input', {'type': 'hidden'}):
          self.params[hidden['name']] = hidden['value']
      else:
        state_num = int(self.params['ICStateNum'])
        self.params['ICStateNum'] = state_num + 1
    except:
      print "error."
    
    if soupify:
      for tag, id in [['label', 'DERIVED_CLSRCH_SSR_CLASS_LBL_LBL'], ['span', 'DERIVED_SSE_DSP_SSR_MSG_TEXT'], ['span', 'DERIVED_CLSRCH_DESCR200']]:
        try:
          print "%s" % self._soup.find(tag, {'id': id}).renderContents()
        except: pass
    else:
      print '---'
    
    return page


class PeopleSoftScraperV2(PeopleSoftScraper):
  def process_subjects(self):
    for subject_code in sorted(self.subjects.keys()):
      self.process_subject(subject_code)
  
  """
  def process_subject(self):
    soup = self._soup
    err = soup.find('span', {'id': 'DERIVED_CLSMSG_ERROR_TEXT'})
    if err:
      print "***** %s" % err.renderContents()
      return
    
    classes = soup.findAll('span', {'class': 'SSSHYPERLINKBOLD'})
    for ind, cls in enumerate(classes):
      self.process_class(cls, ind)
        
    self.params.update({'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH'})
    self._click(self.scrape_url, self.params)
  
  def process_class(self, cls, class_index):
    last_page = False
    while True:
      sections = len(self._soup.find('table', {'id': '$ICField%s$scroll$%s' % (self.ICFieldScroll, class_index)}).find('table').findAll('table'))
      for section_index in range(sections):
        self.process_section(class_index, section_index)
      
      if last_page:
        return
      self.next_class_page(class_index)
      if len(self._soup.findAll('a', {'name': '$ICField65$hdown$%s' % class_index})) == 0:
        last_page = True
  """
  def process_subject(self):
    soup = self._soup
    err = soup.find('span', {'id': 'DERIVED_CLSMSG_ERROR_TEXT'})
    if err:
      print "***** %s" % err.renderContents()
      return
    
    classes = soup.findAll('span', {'class': 'SSSHYPERLINKBOLD'})
    for ind, cls in enumerate(classes):
      page = cls.findNext('span', {'class': 'PSGRIDCOUNTER'}).renderContents()
      number_of_sections = int(re.search('\d+ of (\d+)', page).groups()[0])
      self.process_class(ind, number_of_sections)
        
    self.params.update({'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH'})
    self._click(self.scrape_url, self.params)
  
  def process_class(self, class_index, num_sections):
    last_page = False
    sections_left = num_sections
    for page in range((sections_left / 3) + 1):
      sections_on_page = min(sections_left, 3)
      for section_index in range(sections_on_page):
        try:
          self.process_section(class_index, section_index)
        except Exception, e:
          self._log_error(e)
        self.params.update({'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_BACK'})
        self._click(self.scrape_url, self.params, soupify=False)
      
      sections_left -= sections_on_page
      self.next_class_page(class_index, soupify=False)
  
  def next_class_page(self, class_index, soupify=True):
    self.params.update({
      'ICAction': '$ICField65$hdown$%s' % class_index
    })
    return self._click(self.scrape_url, self.params, soupify)
  
  def process_section(self, class_index, section_index):
    index = (class_index * 3) + section_index
    self.params.update({
      'ICAction': 'DERIVED_CLSRCH_SSR_CLASSNAME_LONG$%s' % index
    })
    page = self._click(self.scrape_url, self.params)
    section_data = self.parse_section(self._soup)
    self.create_section(section_data)
  
  def parse_section(self, soup):
    section_data = {}
    header_bits = soup.find('span', {'id': 'DERIVED_CLSRCH_DESCR200'}).renderContents().replace('&nbsp;', ' ')
    classification, number, section_num, course_name = re.search('(\w+)\s+([\.\w]+) - (\d+) (.+)', header_bits).groups()
    section_data['classification'] = classification
    section_data['classification_name'] = self.subjects[classification]['name']
    section_data['college'] = self.subjects[classification]['college']
    section_data['institution'] = self.institution.slug
    section_data['number'] = number
    section_data['section'] = section_num
    section_data['course_name'] = course_name
    section_data['session'] = self.session.id
    
    section_data['status'] = soup.find('div', {'id': 'win0divSSR_CLS_DTL_WRK_SSR_STATUS_LONG'}).find('img')['alt'].__str__()
    section_data['component'] = soup.find('span', {'id': 'DERIVED_CLSRCH_SSS_PAGE_KEYDESCR'}).renderContents().split('|')[2]
    section_data['grading'] = soup.find('span', {'id': 'GRADE_BASIS_TBL_DESCRFORMAL'}).renderContents()
    section_data['units'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_UNITS_RANGE'}).renderContents().replace(' units', '')
    
    section_data['description'] = self._optional(lambda: soup.find('span', {'id': re.compile('^(DERIVED_CLSRCH_DESCRLONG)|(DERIVED_CLSRCH_SSR_CLASSNOTE_LONG)$')}).renderContents().replace('<br />', ''))
    
    section_data['prof'] = soup.find('span', {'id': 'MTG_INSTR$0'}).renderContents()
    try:
      section_data['notes'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_SSR_REQUISITE_LONG'}).renderContents()
    except: pass
    
    location_bits = soup.find('span', {'id': 'MTG_LOC$0'}).renderContents()
    if location_bits == "TBA":
      location, room = "TBA", ''
    else:
      try:
        location, room = re.search('([\w\s]+) (\w+)', location_bits).groups()
      except:
        location, room = location_bits, ''
    
    datetime_bits = soup.find('span', {'id': 'MTG_SCHED$0'}).renderContents()
    if datetime_bits == "TBA":
      pass
    else:
      days = []
      day_codes = {'Mo': 'Mon', 'Tu': 'Tue', 'We': 'Wed', 'Th': 'Thu', 'Fr': 'Fri', 'Sa': 'Sat', 'Su': 'Sun'}
      for code in day_codes.keys():
        if datetime_bits.find(code) >= 0:
          days.append(day_codes[code])
      start, end = re.search('(\d{1,2}:\d{2}\w{2}) - (\d{1,2}:\d{2}\w{2})', datetime_bits).groups()
      start_time = time.strftime('%H:%M', time.strptime(start, '%I:%M%p'))
      end_time = time.strftime('%H:%M', time.strptime(end, '%I:%M%p'))
      section_data['meetings'] = [{
          'day': day, 'start': start_time, 'end': end_time,
          'location': location, 'room': room
        } for day in days]
    
    
    section_data['mode'] = self._optional(lambda: soup.find('span', {'id': 'INSTRUCT_MODE_DESCR'}).renderContents())# in person / computer / ...
    
    # seat availability
    section_data['level'] = "%s" % self._optional(lambda: soup.find('span', id=re.compile('^PSXLATITEM_XLATLONGNAME$')).renderContents())
    section_data['seats_capacity'] = self._optional(lambda:soup.find('span', {'id': 'SSR_CLS_DTL_WRK_ENRL_CAP'}).renderContents())
    section_data['seats_taken'] = self._optional(lambda:soup.find('span', {'id': 'SSR_CLS_DTL_WRK_ENRL_TOT'}).renderContents())
    section_data['seats_available'] = self._optional(lambda:soup.find('span', {'id': 'SSR_CLS_DTL_WRK_AVAILABLE_SEATS'}).renderContents())
    section_data['waitlist_capacity'] = self._optional(lambda:soup.find('span', {'id': 'SSR_CLS_DTL_WRK_WAIT_CAP'}).renderContents())
    section_data['waitlist_taken'] = self._optional(lambda:soup.find('span', {'id': 'SSR_CLS_DTL_WRK_WAIT_TOT'}).renderContents())
    section_data['waitlist_available'] = self._optional(lambda:int(section_data['waitlist_capacity']) - int(section_data['waitlist_taken']))
    
    class_num = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_CLASS_NBR'}).renderContents()
    section_data['reference_code'] = class_num
    
    return section_data
