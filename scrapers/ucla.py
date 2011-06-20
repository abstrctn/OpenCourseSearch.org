import urllib2, urllib, re, time, itertools
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from django.template.defaultfilters import slugify

from scrapers.general import Scraper

class UCLAScraper(Scraper):
  def __init__(self, *args, **kwargs):
    super(UCLAScraper, self).__init__(*args, **kwargs)
    
    self.term = self.session.system_code
    self.urls = []
  
  def run(self):
    subjects = self._get_subjects()
    print "%s subjects" % len(subjects)
    for subject in subjects:
      courses = self._get_courses(self.term, subject)
      print "  %s courses in %s" % (len(courses), subject['name'])
      for course in courses:
        sections = self._get_sections(self.term, subject, course)
        print "    %s sections in %s" % (len(sections), course['name'])
        for section in sections:
          try:
            data = self._get_section_detail(self.term, section['reference_code'], section)
          except Exception, e:
            self._log_error(e)
          print data
          self.create_section(data)
  
  @classmethod
  def _get_subjects(cls):
    url = 'http://www.registrar.ucla.edu/schedule/schedulehome.aspx'
    soup = BeautifulSoup(urllib2.urlopen(url))
    options = soup.find('select', id='ctl00_BodyContentPlaceHolder_SOCmain_lstSubjectArea').findAll('option')
    subjects = [{'code': option['value'], 'name': option.renderContents().strip() } for option in options]
    return subjects
  
  @classmethod
  def _get_courses(cls, term, subject):
    url = 'http://www.registrar.ucla.edu/schedule/crsredir.aspx?termsel=%s&subareasel=%s' % (term, urllib.quote_plus(subject['code']))
    soup = BeautifulSoup(urllib2.urlopen(url))
    select = soup.find('select', id='ctl00_BodyContentPlaceHolder_crsredir1_lstCourseNormal')
    if not select:
      return []
    options = select.findAll('option')
    courses = [{'code': option['value'], 'name': option.renderContents().split('-')[1].strip() } for option in options]
    return courses
  
  @classmethod
  def _get_sections(cls, term, subject, course):
    url = 'http://www.registrar.ucla.edu/schedule/detselect.aspx?termsel=%s&subareasel=%s&idxcrs=%s' % (term, urllib.quote_plus(subject['code']), urllib.quote_plus(course['code']))
    soup = BeautifulSoup(urllib2.urlopen(url))
    tables = soup.findAll('tr', {'class':'dgdClassDataHeader'})
    sections = [s for s in itertools.chain(*[table.parent.findAll('tr')[1:] for table in tables])]
    data = []
    for section in sections:
      ref_code_link = section.find('td', {'class': 'dgdClassDataColumnIDNumber'}).find('a')
      days = cls._get_cell_value(section, 'dgdClassDataDays')
      if days == "TBA":
        days = ["TBA"]
      if days == "UNSCHED":
        days = []
      if days == "VAR":
        days = ['']
      start = cls._get_cell_value(section, 'dgdClassDataTimeStart')
      end = cls._get_cell_value(section, 'dgdClassDataTimeEnd')
      location = cls._get_cell_value(section, 'dgdClassDataBuilding')
      room = cls._get_cell_value(section, 'dgdClassDataRoom')
      meetings = []
      for day in days:
        meeting = {'day': day, 'location': location, 'room': room}
        if start:
          meeting['start'] = datetime.strftime(datetime.strptime("%sM" % start.rjust(6, '0'), "%I:%M%p"), "%H:%M")
        if end:
          meeting['end'] = datetime.strftime(datetime.strptime("%sM" % end.rjust(6, '0'), "%I:%M%p"), "%H:%M")
        meetings.append(meeting)
      
      if ref_code_link:
        # then it's a complete section record; 
        ref_code_link = ref_code_link['href']
        section_data = {
          'classification': slugify(subject['code']).upper(),
          'classification_name': subject['name'],
          'reference_code': re.search('srs=(\d+)&term', ref_code_link).groups()[0],
          'component': cls._get_cell_value(section, 'dgdClassDataActType'),
          'section': cls._get_cell_value(section, 'dgdClassDataSectionNumber'),
          'seats_taken': cls._get_cell_value(section, 'dgdClassDataEnrollTotal', int),
          'seats_capacity': cls._get_cell_value(section, 'dgdClassDataEnrollCap', int),
          'waitlist_taken': cls._get_cell_value(section, 'dgdClassDataWaitListTotal', int),
          'waitlist_capacity': cls._get_cell_value(section, 'dgdClassDataWaitListCap', int),
          'status': cls._get_cell_value(section, 'dgdClassDataStatus'),
          'course_name': course['name'],
          'meetings': meetings
        }
        data.append(section_data)
      else:
        #otherwise, it's just additional meeting data for the previous record
        data[-1]['meetings'].extend(meetings)
    return data
  
  @classmethod
  def _get_section_detail(cls, term, code, section_data):
    url = 'http://www.registrar.ucla.edu/schedule/subdet.aspx?srs=%s&term=%s' % (code, term)
    soup = BeautifulSoup(urllib2.urlopen(url))
    
    try:
      prof = soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblInstructor').renderContents()
      reversed_profs = [[name.strip() for name in reversed(p.split(','))] for p in re.sub('\s+', ' ', prof).split('/')]
      clean_prof = ", ".join([" ".join(p) for p in reversed_profs])
    except: clean_prof = ''
    
    units = soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblUnits').renderContents()
    clean_units = re.sub('\s(Variable|Alternate)', '', units)
    clean_units = re.sub("\.0", "", clean_units)
    
    section_data.update({
      'units': clean_units,
      'grading': soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblGradingDetail').renderContents().strip().rstrip('.0'),
      'prof': clean_prof,
      'description': soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblCourseDescription').renderContents().strip(),
      'section_name': soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblClassTitle').renderContents().strip(),
      'number': re.search('(\w+)\.', soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblCourseHeader').renderContents()).groups()[0],
      'notes': soup.find('span', id='ctl00_BodyContentPlaceHolder_subdet_lblNotes').renderContents().strip(),
    })
    return section_data
  
  @classmethod
  def _get_cell_value(cls, section, klass, target_klass=None):
    cell = section.find('td', {'class': klass})
    hold = cell
    while True:
      if len(hold.findAll('span')) > 0:
        hold = hold.find('span')
      else:
        value = hold.renderContents().strip()
        if target_klass:
          try:
            return target_klass(value)
          except: return None
        return value


