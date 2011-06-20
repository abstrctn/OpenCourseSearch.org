import cookielib, urllib2, urllib, BeautifulSoup, re, time, pickle, json
from scrapers.general import Scraper
from scrapers.peoplesoft import PeopleSoftScraper, PeopleSoftScraperV2
from scrapers.loader import Loader
from courses.models import *
from pprint import pprint
import time

class OSUScraper(PeopleSoftScraperV2):
  def __init__(self, *args, **kwargs):
    super(OSUScraper, self).__init__(*args, **kwargs)
    
    self.params.update({
      'CLASS_SRCH_WRK2_INSTITUTION$46$': self.institution_code,
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY': 'N',
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY$chk': 'N',
      'CLASS_SRCH_WRK2_ACAD_CAREER': 'UGRD',
      'CLASS_SRCH_WRK2_CAMPUS': 'COL',
    })
    self.home_url = 'https://courses.osu.edu/psc/hcosuct/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL&PortalContentProvider=HRMS&PortalCRefLabel=Class%20Search&PortalRegistryName=EMPLOYEE&PortalServletURI=https://courses.osu.edu/psp/hcosuct/&PortalURI=https://courses.osu.edu/psc/hcosuct/&PortalHostNode=HRMS&NoCrumbs=yes&PortalKeyStruct=null'
    self.scrape_url = 'https://courses.osu.edu/psc/hcosuct/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL'
    self.ICFieldScroll = '65'
  
  def run(self, forever=False):
    self._click(self.home_url) # touch home
    self.set_term()
    self.parse_subjects(self._soup)
    self.process_subjects()
  
  def set_term(self):
    print "Setting term..."
    
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_SRCH$56$',
      'ICAjax': '1',
      'ICActionPrompt': 'false',
      'CLASS_SRCH_WRK2_STRM$48$': self.term,
      'CLASS_SRCH_WRK2_INSTITUTION$46$': self.institution_code
    })
    page = self._click(self.scrape_url, self.params)
  
  def parse_subjects(self, soup):
    javascript = soup.findAll('script')[2].contents[0]
    javascript = javascript.replace('\n', '').replace('\t', '').replace('&amp;', '&').replace('"', "*****").replace("'", '"').replace("*****", "'")
    items = re.search('optionsArray_win0 = (.+);var', javascript).groups()[0]
    subjects = json.loads(items)[1][1:] #[CODE, Name]
    
    data = {}
    for subject in subjects:
      data[subject[0]] = {'name': subject[1], 'college': ''}

    self.subjects = data
    print "  Finished."
    return soup
  
  def process_subject(self, section_code):
    print "Processing %s" % section_code
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH',
      'CLASS_SRCH_WRK2_SUBJECT': section_code,
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY$chk': 'N',
      'CLASS_SRCH_WRK2_ACAD_CAREER': '', # all levels
    })
    self._click(self.scrape_url, self.params)
    soup = self._soup
    
    super(OSUScraper, self).process_subject()
  
  # Do any processing of the section data on top of the standard PeopleSoft parser
  def parse_section(self, soup):
    section_data = super(OSUScraper, self).parse_section(soup)
    section_data['level'] = "%s" % soup.find('span', id='PSXLATITEM_XLATLONGNAME$56$').renderContents()
    return section_data

class OSUScraperOld(PeopleSoftScraper):
  def __init__(self, *args, **kwargs):
    self.short_code = 'osu'
    super(OSUScraper, self).__init__(*args, **kwargs)
    
    self.params.update({
      'CLASS_SRCH_WRK2_INSTITUTION$46$': self.institution_code,
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY': 'N',
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY$chk': 'N',
      'CLASS_SRCH_WRK2_ACAD_CAREER': 'UGRD',
      'CLASS_SRCH_WRK2_CAMPUS': 'COL',
    })
    #self.home_url = 'https://courses.osu.edu/psc/hcosuct/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?PortalActualURL=https%3a%2f%2fcourses.osu.edu%2fpsc%2fhcosuct%2fEMPLOYEE%2fHRMS%2fc%2fCOMMUNITY_ACCESS.CLASS_SEARCH.GBL&amp;PortalContentURL=https%3a%2f%2fcourses.osu.edu%2fpsc%2fhcosuct%2fEMPLOYEE%2fHRMS%2fc%2fCOMMUNITY_ACCESS.CLASS_SEARCH.GBL&amp;PortalContentProvider=HRMS&amp;PortalCRefLabel=Class%20Search&amp;PortalRegistryName=EMPLOYEE&amp;PortalServletURI=https%3a%2f%2fcourses.osu.edu%2fpsp%2fhcosuct%2f&amp;PortalURI=https%3a%2f%2fcourses.osu.edu%2fpsc%2fhcosuct%2f&amp;PortalHostNode=HRMS&amp;NoCrumbs=yes&amp;PortalKeyStruct=null'
    self.home_url = 'https://courses.osu.edu/psc/hcosuct/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL&PortalContentProvider=HRMS&PortalCRefLabel=Class%20Search&PortalRegistryName=EMPLOYEE&PortalServletURI=https://courses.osu.edu/psp/hcosuct/&PortalURI=https://courses.osu.edu/psc/hcosuct/&PortalHostNode=HRMS&NoCrumbs=yes&PortalKeyStruct=null'
    self.scrape_url = 'https://courses.osu.edu/psc/hcosuct/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL'
    
    self.institution = Institution.objects.get(short_code=self.short_code)
    self.session, created = Session.objects.get_or_create(
        institution=self.institution,
        name='Fall 2011',
        start_date=datetime.datetime(2011,9,6),
        end_date=datetime.datetime(2011,12,16))
    self.loader = Loader(self.session)
    
    self.timers = {'default': datetime.datetime.now()}
  
  def run(self, forever=False):
    self._click(self.home_url) # touch home
    return self.set_term()
  
  def set_term(self):
    print "Setting term..."
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_SRCH$56$',
      'ICAjax': '1',
      'ICActionPrompt': 'false',
      'CLASS_SRCH_WRK2_STRM$48$': self.term,
    })
    page = self._click(self.scrape_url, self.params)
    return self.parse_subjects(page)
  
  def parse_subjects(self, page):
    print "Parsing subjects..."
    """
    Gathers list of all colleges, and their corresponding class sections.
    Writes full list out to 'colleges-classifications.txt':
    data = [
      ["College of Arts and Science", "Biology", "BIOL-UA"],
      ...
    ]
    """
    soup = BeautifulSoup.BeautifulSoup(page)
    #javascript = soup.find('genscript', {'id': 'script'}).contents[0]
    javascript = soup.findAll('script')[2].contents[0]
    javascript = javascript.replace('\n', '').replace('\t', '').replace('&amp;', '&').replace('"', "*****").replace("'", '"').replace("*****", "'")
    items = re.search('optionsArray_win0 = (.+);var', javascript).groups()[0]
    subjects = json.loads(items)[1][1:] #[CODE, Name]
    
    data = {}
    for subject in subjects:
      data[subject[0]] = {'name': subject[1], 'college': ''}
      #data.append(['_default', subject[0], subject[1]])
    
    #f = open('%scollege-classifications.txt' % (self.storage_dir), 'w')
    #pickle.dump(data, f)
    #f.close()

    self.subjects = data
    print "  Finished."
    return soup
  
  def process_subjects(self):
    for subject_code in self.subjects.keys():
      self.process_subject(subject_code)
  
  def process_subject(self, section_code):
    print "Processing %s" % section_code
    self.params.update({
      'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH',
      'CLASS_SRCH_WRK2_SUBJECT': section_code,
      'CLASS_SRCH_WRK2_SSR_OPEN_ONLY$chk': 'N',
      'CLASS_SRCH_WRK2_ACAD_CAREER': '', # all levels
    })
    page = self._click(self.scrape_url, self.params)
    soup = BeautifulSoup.BeautifulSoup(page)
    
    classes = soup.findAll('span', {'class': 'SSSHYPERLINKBOLD'})
    for ind, cls in enumerate(classes):
      self.process_class(cls, ind)
    
    # additional pages of classes?
    
    self.params.update({'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH'})
    self._click(self.scrape_url, self.params)
    return page
  
  def process_class(self, cls, class_index):
    last_page = False
    while True:
      sections = len(self._soup.find('table', {'id': '$ICField65$scroll$%s' % class_index}).find('table').findAll('table'))
      for section_index in range(sections):
        self.process_section(class_index, section_index)
      
      if last_page:
        return
      self.next_class_page(class_index)
      if len(self._soup.findAll('a', {'name': '$ICField65$hdown$%s' % class_index})) == 0:
        last_page = True
  
  def next_class_page(self, class_index):
    self.params.update({
      'ICAction': '$ICField65$hdown$%s' % class_index
    })
    return self._click(self.scrape_url, self.params)
  
  def process_section(self, class_index, section_index):
    index = (class_index * 3) + section_index
    self.params.update({
      'ICAction': 'DERIVED_CLSRCH_SSR_CLASSNAME_LONG$%s' % index
    })
    #print "  %s" % 'DERIVED_CLSRCH_SSR_CLASSNAME_LONG$%s' % index
    page = self._click(self.scrape_url, self.params)
    soup = BeautifulSoup.BeautifulSoup(page)
    
    section_data = {}
    header_bits = soup.find('span', {'id': 'DERIVED_CLSRCH_DESCR200'}).renderContents().replace('&nbsp;', ' ')
    classification, number, section_num, course_name = re.search('(\w+)\s+([\.\w]+) - (\d+) ([\w\s]+)', header_bits).groups()
    section_data['classification'] = classification
    section_data['classification_name'] = self.subjects[classification]['name']
    section_data['college'] = self.subjects[classification]['college']
    section_data['institution'] = self.short_code
    section_data['number'] = number
    section_data['section'] = section_num
    section_data['course_name'] = course_name
    section_data['session'] = self.session.id
    
    section_data['status'] = soup.find('div', {'id': 'win0divSSR_CLS_DTL_WRK_SSR_STATUS_LONG'}).find('img')['alt'].__str__()
    section_data['component'] = soup.find('span', {'id': 'DERIVED_CLSRCH_SSS_PAGE_KEYDESCR'}).renderContents().split('|')[2]
    section_data['grading'] = soup.find('span', {'id': 'GRADE_BASIS_TBL_DESCRFORMAL'}).renderContents()
    section_data['units'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_UNITS_RANGE'}).renderContents().replace(' units', '')
    
    section_data['description'] = soup.find('span', {'id': 'DERIVED_CLSRCH_DESCRLONG'}).renderContents().replace('<br />', '')
    section_data['prof'] = soup.find('span', {'id': 'MTG_INSTR$0'}).renderContents()
    try:
      section_data['notes'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_SSR_REQUISITE_LONG'}).renderContents()
    except: pass
    
    datetime_bits = soup.find('span', {'id': 'MTG_SCHED$0'}).renderContents()
    if datetime_bits == "TBA":
      pass
    else:
      section_data['days'] = []
      day_codes = {'Mo': 'Mon', 'Tu': 'Tue', 'We': 'Wed', 'Th': 'Thu', 'Fr': 'Fri', 'Sa': 'Sat', 'Su': 'Sun'}
      for code in day_codes.keys():
        if datetime_bits.find(code) >= 0:
          section_data['days'].append(day_codes[code])
      start, end = re.search('(\d{1,2}:\d{2}\w{2}) - (\d{1,2}:\d{2}\w{2})', datetime_bits).groups()
      section_data['start_time'] = time.strftime('%H:%M', time.strptime(start, '%I:%M%p'))
      section_data['end_time'] = time.strftime('%H:%M', time.strptime(end, '%I:%M%p'))
    
    location_bits = soup.find('span', {'id': 'MTG_LOC$0'}).renderContents()
    if location_bits == "TBA":
      pass
    else:
      location, room = re.search('([\w\s]+) (\w+)', location_bits).groups()
      section_data['location'] = location
      section_data['room'] = room
    section_data['mode'] = soup.find('span', {'id': 'INSTRUCT_MODE_DESCR'}).renderContents()# in person / computer / ...
    
    # seat availability
    section_data['level'] = "%s" % soup.find('span', {'id': 'PSXLATITEM_XLATLONGNAME$56$'}).renderContents()
    section_data['seats_capacity'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_ENRL_CAP'}).renderContents()
    section_data['seats_taken'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_ENRL_TOT'}).renderContents()
    section_data['seats_available'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_AVAILABLE_SEATS'}).renderContents()
    section_data['waitlist_capacity'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_WAIT_CAP'}).renderContents()
    section_data['waitlist_taken'] = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_WAIT_TOT'}).renderContents()
    #pprint(section_data)
    
    class_num = soup.find('span', {'id': 'SSR_CLS_DTL_WRK_CLASS_NBR'}).renderContents()
    section_data['id'] = class_num
    
    print "Server time:\t%s" % (datetime.datetime.now() - self.timers['default'])
    self.timers['default'] = datetime.datetime.now()
    
    create_section(section_data)
    
    print "ORM time:\t%s" % (datetime.datetime.now() - self.timers['default'])
    self.timers['default'] = datetime.datetime.now()
    
    #self.classes[class_num] = section_data
    
    self.params.update({'ICAction': 'CLASS_SRCH_WRK2_SSR_PB_BACK'})
    self._click(self.scrape_url, self.params)

