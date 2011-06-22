import urllib2, urllib, re, time
from BeautifulSoup import BeautifulSoup

from scrapers.flatpage import FlatpageScraper

#http://www.college.columbia.edu/unify/bulletinSearch.php?school=CC&header=www.college.columbia.edu/include/popup_header.php&subjectVar=AMST&termVar=x

class ColumbiaScraper(FlatpageScraper):
  def __init__(self, *args, **kwargs):
    super(ColumbiaScraper, self).__init__(*args, **kwargs)
  
  def get_all_urls(self):
    # get list of all subjects
    page = urllib2.urlopen('http://www.columbia.edu/cu/bulletin/uwb/subj/').read()
    subject_codes = re.findall(">([A-Z]{4})\/<", page)
    print "%s subjects found." % len(subject_codes)
    
    for subject in subject_codes:
      # get list of all courses in subject
      page = urllib2.urlopen('http://www.columbia.edu/cu/bulletin/uwb/subj/%s/' % subject).read()
      course_codes = re.findall(">(\w+-%s-\w+)\/<" % self.session.system_code, page)
      
      for course in course_codes:
        self.urls.append('http://www.columbia.edu/cu/bulletin/uwb/subj/%s/%s/' % (subject, course))
      
      print "%s courses found in %s." % (len(course_codes), subject)
    
    print "%s courses found total." % len(self.urls)
  
  def parse_url(self, url, soup):
    section_data = {
      'classification': url.split('/')[-2],
      'institution': self.institution.slug,
      'course_name': soup.find('font', size='+2').renderContents(),
      'session': self.session.id,
      'status': 'Open', # default to Open - doesn't specify when there's space
      #'grading'
      #'description'
      #'notes'
      #'days'
      #'start_time'
      #'end_time'
      #'location'
      #'room'
      #'mode'
      #'waitlist_capacity'
      #'waitlist_taken'
      #'waitlist_available'
    }
    notes = []
    for row in soup.findAll('tr td', bgcolor='#99CCFF'):
      key = row.find('font', size="+1").renderContents()
      value = row.parent.find('td', bgcolor="#DADADA")
      if key == "Call Number":
        section_data['reference_code'] = value
      if key == "Points":
        section_data['units'] = value
      if key == "Instructor":
        section_data['prof'] = value
      if key == "Type":
        section_data['component'] = value
      if key == "Subject":
        section_data['classification_name'] = value
      if key == "Section":
        section_data['section'] = value
      if key == "Division":
        section_data['college'] = value
      if key == "Number":
        section_data['number'] = value
      if key == "Status":
        if value == 'Full':
          section_data['status'] = 'Closed' 
      if key == "Enrollment":
        section_data['seats_taken'] = value.split(' student')[0]
        capacity = re.search('\((\d+) max\)', s).groups()
        if capacity:
          section_data['seats_capacity'] = capacity[0]
          section_data['seats_available'] = int(capacity[0]) - int(section_data['seats_taken'])
      if key == "Note":
        notes.append(value)
    
    section_data['notes'] = " ".join(notes)
    
