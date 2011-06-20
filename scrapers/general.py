from api.helpers import create_section
from django.conf import settings
from networks.models import Network
from django.template.defaultfilters import slugify

class Scraper(object):
  def __init__(self, *args, **kwargs):
    self.debug = kwargs.get('debug', False)
    self.processed = 0
    self._set_session(**kwargs)
    open(settings.LOG_ROOT + '%s_%s_errors.log' % (self.network.slug, self.session.slug), 'w').close()
    self._log_error('test')
  
  def _log_error(self, e):
    f = open(settings.LOG_ROOT + '%s_%s_errors.log' % (self.network.slug, self.session.slug), 'a')
    f.write('%s' % e)
    f.close()
  
  def _set_session(self, **kwargs):
    try:
      self.network = Network.objects.get(slug=kwargs.get('network'))
      self.session = kwargs.get('session', None)
      self.institution = self.network.institution
      try:
        self.institution_code = self.session.sessioninfo_set.get(info_type='institution').info_value
      except: pass
    except Exception, e:
      self._log_error(e)
  
  def create_section(self, section_data):
    section_data['network'] = self.network.slug
    section_data['institution'] = self.network.institution.slug
    section_data['session'] = self.session.id
    self.processed += 1
    print "*** %s sections processed." % self.processed
    result = create_section(section_data)

  def _optional(self, l):
    try:
      return l()
    except: return None

"""
  section_data = {
      'classification'              'ACCT'
      'classification_name'         'Accounting'
      'college'                     'College of Arts and Science'
      'institution'                 'nyu'
      'number'                      '101'
      'section'                     '001'
      'course_name'                 'Introductory Finance'
      'session'                     id of Session record
      'status'                      'Open'
      'component'                   'Lecture'
      'grading'                     'A-E'
      'units'                       '5'
      'description'                 'Lorem ipsum dolor.'
      'prof'                        'Katie Roiphe'
      'notes'                       'Lorem ipsum dolor.'
      'days'                        'Mon,Tue,Wed'
      'start_time'                  '10:30'
      'end_time'                    '16:30'
      'location'                    'Building'
      'room'                        '40W'
      'mode'                        'Computer'
      'seats_capacity'               int
      'seats_taken'                  int
      'seats_available'              int
      'waitlist_capacity'            int
      'waitlist_taken'               int
      'waitlist_available'           int
      'reference_code'              School's internal id
    }
"""