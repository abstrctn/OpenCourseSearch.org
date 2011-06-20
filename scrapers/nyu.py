import cookielib, urllib2, urllib, BeautifulSoup, re, time, pickle
from scrapers.peoplesoft import PeopleSoftScraper
from courses.models import *

class NYUScraper(PeopleSoftScraper):
  def __init__(self, *args, **kwargs):
    super(NYUScraper, self).__init__(*args, **kwargs)
    
    self.season = self.session.sessioninfo_set.get(info_type='season').info_value
    self.params.update({
      'NYU_CLS_DERIVED_DESCR100': '',
      'NYU_CLS_DERIVED_DESCR100_JOB_POST1': '',
      'NYU_CLS_WRK_NYU_%s' % self.season: 'Y',
      'NYU_CLS_WRK_NYU_%s$chk' % self.season: 'Y',
    })
    self.login_url = 'https://admin.portal.nyu.edu/psp/paprod/EMPLOYEE/EMPL/?cmd=login'
    self.scrape_url = 'https://sis.nyu.edu/psc/csprod/EMPLOYEE/CSSS/c/NYU_SR.NYU_CLS_SRCH.GBL'
  
  def run(self, forever=False):
    self._make_connection()
    if self.end_index:
      end = self.end_index
    else:
      end = len(self.sections)
    while True:
      for i in range(self.start_index, end):
        print "Section %s." % i
        self.process_section(i)
      if not forever:
        return
  
  def _make_connection(self):
    self.access_home()
    self.set_term()
    print "retrieving course sections..."
    self.get_all_sections()
  
  def set_term(self):
    params = {
      'ICAction': 'NYU_CLS_DERIVED_NYU_CLS_YR_%s' % self.term,
    }
    self._click(self.scrape_url)
  
  def log_in(self):
    params = {
      'timezoneOffset': '240',
      'httpPort': '',
      'userid': self.username,
      'pwd': self.password,
      'Submit': 'Sign In'
    }
    self._click(self.login_url)
    self._click(self.login_url, data)
    print "logged in."
  
  def access_home(self):
    self._click(self.scrape_url)
    soup = self._soup
    self.ICSID = soup.find('input', {'type': 'hidden', 'name': 'ICSID'})['value']
    print "Browsing key found: %s" % self.ICSID
  
  def get_home(self):
    self.params.update({
      'ICStateNum': '1',
      'ICAction': 'NYU_CLS_DERIVED_BACK',
      'ICSID': self.ICSID,
      'NYU_CLS_WRK_NYU_%s' % self.season: 'Y',
      'NYU_CLS_WRK_NYU_%s$chk' % self.season: 'Y',
    })
    self._click(self.scrape_url, self.params)
    
    self.params.update({
      'ICAction': 'NYU_CLS_WRK_NYU_%s' % self.season,
      'ICSID': self.ICSID,
      'NYU_CLS_WRK_NYU_%s' % self.season: 'Y',
      'NYU_CLS_WRK_NYU_%s$chk' % self.season: 'Y',
    })
    self._click(self.scrape_url, self.params)

    return self._soup
  
  def get_all_sections(self):
    """
    Gathers list of all colleges, and their corresponding class sections.
    Writes full list out to 'colleges-classifications.txt':
    data = [
      ["College of Arts and Science", "Biology", "BIOL-UA"],
      ...
    ]
    """
    soup = self.get_home()
    
    divs = soup.findAll('a', {'class': 'SSSAZLINK'})
    ret = []
    for i in divs:
      ret.append([i['id'], i.contents[0]])
    self.sections = ret[1:]
    print "%s sections loaded" % (len(self.sections))
    
    # get colleges, classifications
    #data = []
    data = {}
    ret = []
    colleges = soup.findAll('td', {'class': 'SSSGROUPBOXLEFTLABEL'})
    colleges.reverse()
    for c in colleges:
      college = c.contents[1]
      college = college.replace('&nbsp;', '')
      table = c.findNext('table', {'class': 'SSSGROUPBOXLEFT'})
      classifications = table.findAll('a', {'class': 'SSSAZLINK'})
      for cls in classifications:
        name = " ".join(["%s" % i for i in cls.contents])
        name = name.replace('<br />', '')
        name = name.replace('&amp;', '&')
        try:
          course_name, course_code = re.search('(.*)\s\((.+)\)', name).groups()
          #data.append([college, course_name, course_code])
          data[course_code] = {'college': college, 'name': course_name}
        except:
          print name
    self.classifications = data
    #f = open('%scollege-classifications.txt' % (self.storage_dir), 'w')
    #pickle.dump(data, f)
    #f.close()
    
  def _confirm_long_listing(self, ICStateNum):
    # basically, press "yes" to confirm showing more than 100 results
    self.params.update({'ICStateNum': ICStateNum, 'ICAction': '#ICYes', 'ICSID': self.ICSID})
    self._click(self.scrape_url, self.params)
    return self._soup
  
  def get_section_listing(self, id, current_only='Y'):
    self.params.update({'ICStateNum': '1', 'ICAction': id, 'ICSID': self.ICSID})
    self._click(self.scrape_url, self.params)
    soup = self._soup
    ICStateNum = 1 # default
    
    if self._page.find("This search will return more than 100 results and may take a while to process.") > 0:
      print "confirming long listing..."
      #time.sleep(4)
      self.longs.append(id)
      ICStateNum = int(soup.find('input', {'type': 'hidden', 'name': 'ICStateNum'})['value'])
      print 'ICStateNum found: %s' % ICStateNum
      
      soup = self._confirm_long_listing(ICStateNum)
      print "long listing retrieved."
    
    if not self.section_data.has_key(id):
      self.section_data[id] = {}
    self._list_courses_in_section(id, soup, current_only)
    print "%s classes gathered from %s" % (len(self.section_data[id].keys()), id)
    self.last_section = id
    return ICStateNum
  
  def _list_courses_in_section(self, id, soup, current_only):
    ret = {}
    classes = soup.findAll('span',
        {'style': "background-color: white; font-family: arial; color: black; font-size: 16px; font-weight: normal"})
    for c in classes:
      try:
        bits = [i.strip() for i in re.split(' (\d+)', c.find('b').contents[0])]
        classification = bits[0]
        number = bits[1]
        name = " ".join(bits[2:])
      except:
        classification, number, name = None, None, None
      
      description, meta, college, units, level = '', '', '', '', ''
      try:
        description = c.find('div', {'class': 'courseDescription'}).find('p').contents[0]
      except: pass
      try:
        meta = c.findNext('span', {'class': 'SSSTEXTBLUE'}).contents[0].split('|')
      except: pass
      try:
        college = meta[0].strip()
      except: pass
      try:
        units = meta[1].split(':')[1].strip()
      except: pass
      try:
        level = meta[2].split(':')[1].strip()
      except: pass
      self.save = soup
      try:
        index = c.findNext('td', {'class': 'SSSGROUPBOXRIGHTLABEL'}).findNext('a')['name'].split('$')[1]
      except:
        # when there is a "more description" link
        index = None
        
      self.section_data[id]["%s-%s" % (classification, number)] = {
          'classification': classification,
          'name': name,
          'description': description,
          'number': number, 
          'college': college, 
          'units': units, 
          'level': level, 
          'index': index}
  
  def process_section(self, id):
    id = self.sections[id][0]
    hold = len(self.classes.keys())
    ICStateNum = self.get_section_listing(id) + 1
    keys = {}
    for key in self.section_data[id].keys():
      # uniquify it
      keys[key] = 1
    total = len(keys.keys())
    for i, key in enumerate(sorted(keys.keys())):
      ind = self.section_data[id][key]['index']
      if ind:
        print "  grabbing course %s of %s..." % (i + 1, total)
        self.get_detail_for_course_in_section(id, ind, ICStateNum)
    print "%s classes processed" % (len(self.classes.keys()) - hold)
    print "%s total classes scraped" % len(self.classes.keys())
    #f = open('%s%s.txt' % (self.storage_dir, id), 'w')
    #pickle.dump(self.classes, f)
    #f.close()
    #self.classes = {}
      
  
  def get_detail_for_course_in_section(self, id, ind, ICStateNum):
    self.params.update({'ICStateNum': ICStateNum, 'ICAction': 'NYU_CLS_DERIVED_TERM$' + ind, 'ICSID': self.ICSID})
    self._click(self.scrape_url, self.params)
    #try:
    self.summarize_detail(id, self._soup)
    #except Exception, e:
    #  self._log_error(e)
  
  def summarize_detail(self, id, soup):
    tables = soup.find('table', {'class': 'PSLEVEL3SCROLLAREABODY'}).findAll('table', {'class': 'PSGROUPBOX', 'width': '531'})
    notes = ''
    for table in tables:
      datacell = table.find('td', {'style': 'background-color: white; font-family: arial; font-size: 12px;'})
      self.datacell = datacell
      
      if ("%s" % datacell).find("<b>Topic: </b>") > 0:
        # Topics class. Special case.
        classification, number = re.split('\s+',
            re.search('([-\w]+\s+\d+)', "%s" % datacell.find('p')).groups()[0])
        class_name = re.search('<b>Topic: </b>(.*)<p>', "%s" % datacell).groups()[0].strip()
      else:
        # Normal case.
        bits = re.split('\s+', re.search('([-\w\s.]+\s+\d+)', "%s" % datacell).groups()[0])
        number = bits[-1]
        classification = " ".join(bits[:-1])
        class_name = ''
      try:
        units = re.search('([-\w]+ units)', "%s" % datacell).groups()[0]
      except:
        try:
          # leftover units from previous session of same class, use
          if units:
            pass
          else:
            units = ""
        except:
          units = self.section_data[id]["%s-%s" % (classification, number)]['units']
      
      for i in datacell.findAll('span'):
        if i.contents:
          if i.renderContents() == "Class#:":
            classnum = i.nextSibling.strip(' |')
          if i.renderContents() == "Session:":
            session = i.nextSibling.strip(' |')
          if i.renderContents() == "Section:":
            section = i.nextSibling.strip(' |\r\n')
          if i.renderContents() == "Class Status:":
            status = i.nextSibling.nextSibling.renderContents()
          elif i.renderContents() == "Grading:":
            grading = i.nextSibling.strip()
          elif i.renderContents() == "<b>Course Location Code: </b>":
            loccode = i.nextSibling.strip(' |')
            component = i.nextSibling.nextSibling.nextSibling.strip()
          elif i.renderContents() == "<b>Notes: </b>":
            notes = i.nextSibling.strip()
      
      try:
        meet_data = re.search('(\d{2}/\d{2}/\d{4}[^<]*(at[^<]*)?(with[^<]*)?)\r', "%s" % datacell).groups()[0].strip(' \r\n')
      except:
        self.save = datacell
      
      try:
        days = re.search('(([A-Z][a-z][a-z],?){1,3})', meet_data).groups()[0].split(',')
      except: days = []
      try:
        start, end = re.search('(\d{1,2}\.\d{2} \w{2})[^\d]*(\d{1,2}\.\d{2} \w{2})', meet_data).groups()
        if len(start) == 7:
          start = "0%s" % start
        if len(end) == 7:
          end = "0%s" % end
        if start[-2:] == "PM" and start[:2] != '12':
          start = datetime.time(int(start[:2]) + 12, int(start[3:5]))
        else:
          start = datetime.time(int(start[:2]), int(start[3:5]))
        if end[-2:] == "PM" and end[:2] != '12':
          end = datetime.time(int(end[:2]) + 12, int(end[3:5]))
        else:
          end = datetime.time(int(end[:2]), int(end[3:5]))
      except:
        pass
      
      try:
        prof_list = re.search('with (.*)', meet_data).groups()[0]
        try:
          profs = [[name.strip() for name in reversed(prof.split(','))] for prof in prof_list.split(';')]
          prof = ", ".join([" ".join(prof) for prof in profs])
        except:
          prof = prof_list
      except:
        prof = ''
      
      
      try:
        location, room = re.search('at (\w+) (\w+) with', "%s" % datacell).groups()
      except:
        location, room = '', ''
      
      """
      self.classes[classnum] = {
        'classification': "%s" % classification,
        'number': "%s" % number,
        'status': "%s" % status,
        'session': "%s" % session,
        'section': "%s" % section,
        'grading': "%s" % grading,
        'loc_code': "%s" % loccode,
        'component': "%s" % component,
        'meet_data': "%s" % meet_data,
        'notes': "%s" % notes,
        'level': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['level'],
        'course_name': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['name'],
        'college': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['college'],
        'description': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['description'],
        'class_name': "%s" % class_name,
        'units': "%s" % units,
      }
      """
      
      section_data = {}
      section_data['reference_code'] = classnum
      section_data['classification'] = classification.replace(' ', '')
      section_data['college'] = "%s" % self.section_data[id]["%s-%s" % (classification, number)]['college']
      section_data['institution'] = self.institution.slug
      section_data['number'] = number
      section_data['section'] = section
      section_data['course_name'] = "%s" % self.section_data[id]["%s-%s" % (classification, number)]['name']
      section_data['session'] = self.session.id
      section_data['section_name'] = class_name
      
      section_data['status'] = status
      section_data['component'] = component
      section_data['grading'] = grading
      section_data['units'] = units.replace('units', '')
      
      section_data['description'] = "%s" % self.section_data[id]["%s-%s" % (classification, number)]['description']
      section_data['notes'] = notes
      section_data['prof'] = prof
      
      section_data['meetings'] = []
      for day in days:
        meeting = {'day': day, 'location': location, 'room': room}
        try:
          start, end = re.search('(\d{1,2}\.\d{2} \w{2})[^\d]*(\d{1,2}\.\d{2} \w{2})', meet_data).groups()
          start = time.strftime('%H:%M', time.strptime(start, '%I.%M %p'))
          end = time.strftime('%H:%M', time.strptime(end, '%I.%M %p'))
          meeting.update({'start': start, 'end': end})
        except: pass # start, end not known
        section_data['meetings'].append(meeting)
      """
      try:
        start, end = re.search('(\d{1,2}\.\d{2} \w{2})[^\d]*(\d{1,2}\.\d{2} \w{2})', meet_data).groups()
        start = time.strftime('%H:%M', time.strptime(start, '%I.%M %p'))
        end = time.strftime('%H:%M', time.strptime(end, '%I.%M %p'))
        section_data['meetings'] = [{'day': day, 'start': start, 'end': end} for day in days]
      except: pass
      """
      """
      section_data['days'] = days
      try:
        start, end = re.search('(\d{1,2}\.\d{2} \w{2})[^\d]*(\d{1,2}\.\d{2} \w{2})', meet_data).groups()
        section_data['start_time'] = time.strftime('%H:%M', time.strptime(start, '%I.%M %p'))
        section_data['end_time'] = time.strftime('%H:%M', time.strptime(end, '%I.%M %p'))
      except: pass
      """
      
      #section_data['location'] = location
      #section_data['room'] = room
      
      section_data['classification_name'] = self.classifications[classification]['name']
      #section_data['mode'] = 
      section_data['level'] = "%s" % self.section_data[id]["%s-%s" % (classification, number)]['level']
      
      self.create_section(section_data)

    
    return True
