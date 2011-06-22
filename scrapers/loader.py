import pickle, re, os
from courses.models import *

class Loader(object):
  def __init__(self, session):
    self.institution = session.institution
    self.session = session
    self.short_code = self.institution.short_code
  
  def load_classifications(self):
    f = open('/opt/django-projects/ocs/storage/%s/college-classifications.txt' % self.short_code)
    data = pickle.load(f)
    for i in data:
      print i
      cllg, classification_name, classification_code = i
      college, created = College.objects.get_or_create(name = cllg)
      c, created = Classification.objects.get_or_create(
          name = classification_name,
          code = classification_code,
          college=college)
      print created
  
  def load_all_listings(self):
    from courses.helpers import *
    for f in os.listdir('/opt/django-projects/ocs/storage/'):
      try:
        t = re.search('(LINK\d\$\d{1,3}).txt', f).groups()[0]
        load_listing(t)
      except Exception, e:
        print e
    
  def load_listing(self, key):
    f = open('/opt/django-projects/ocs/storage/%s.txt' % key)
    data = pickle.load(f)
    
    _created_course = 0
    _updated_course = 0
    _skipped_course = 0
    _created_section = 0
    _updated_section = 0
    _skipped_section = 0
    for id in data.keys():
      try:
        c = data[id]
        c = self.clean(c)
        start, end = None, None
        
        number = c['number']
        try:
          CLASSIFICATION, created = Classification.objects.get_or_create(code=c['classification'])
        except:
          CLASSIFICATION = Classification.objects.filter(code=['classification'])[0]
        COLLEGE, created = College.objects.get_or_create(
            institution=self.institution,
            name=c['college']
        )
        
        start = c['start_time']
        end = c['end_time']
        days = c['days']
        
        # get or create the course
        qs = Course.objects.filter(
            institution = self.institution,
            classification = CLASSIFICATION,
            number = number)
        if qs.count() > 0:
          COURSE = qs[0]
          #print "Course found."
          updated = False
          if c['loc_code'] and c['loc_code'] != COURSE.location_code:
            COURSE.location_code = c['loc_code']
            updated = True
          if c['course_name'] and c['course_name'] != COURSE.course_name:
            COURSE.course_name = c['course_name']
            updated = True
          if c['description'] and c['description'] != COURSE.description:
            COURSE.description = c['description']
            updated = True
          if updated:
            COURSE.save()
            #print "  Course updated"
            _updated_course += 1
          else:
            _skipped_course += 1
        else:
          COURSE = Course(
            institution = self.institution,
            session = self.session,
            classification = CLASSIFICATION,
            number = int(number),
            level = c['level'],
            component = c['component'][:20],
            grading = c['grading'][:20],
            location_code = c['loc_code'],
            course_name = c['course_name'],
            college = COLLEGE,
            description = c['description'],
          )
          COURSE.save()
          #print "Course created: %s" % COURSE
          _created_course += 1
        
        # create the section
        qs = Section.objects.filter(course = COURSE, section = c['section'])
        if qs.count() > 0:
          SECTION = qs[0]
          #print "Section found: %s" % SECTION
          updated = False
          if id != SECTION.number:
            SECTION.number = id
            updated = True
          if c['is_open'] and c['is_open'] != SECTION.is_open:
            SECTION.is_open = c['is_open']
            updated = True
          if prof and prof != SECTION.prof:
            SECTION.prof = prof
            updated = True
          if c['units'] and c['units'] != SECTION.units:
            SECTION.units = c['units']
            updated = True
          if c['class_name'] and c['class_name'] != SECTION.class_name:
            SECTION.class_name = c['class_name']
            updated = True
          if c['notes'] and c['notes'] != SECTION.notes:
            SECTION.notes = c['notes']
            updated = True
          if updated:
            SECTION.save()
            #print "  Section updated"
            _updated_section += 1
          else:
            _skipped_section += 1
        else:
          SECTION = Section(
            institution = self.institution,
            course = COURSE,
            is_open = c['is_open'],
            class_name = c['class_name'],
            notes = c['notes'],
            section = c['section'],
            prof = prof,
            number = id,
            units = c['units'],
          )
          if 'Mon' in days:
            SECTION.meet_mon_start = start
            SECTION.meet_mon_end = end
          if 'Tue' in days:
            SECTION.meet_tue_start = start
            SECTION.meet_tue_end = end
          if 'Wed' in days:
            SECTION.meet_wed_start = start
            SECTION.meet_wed_end = end
          if 'Thu' in days:
            SECTION.meet_thu_start = start
            SECTION.meet_thu_end = end
          if 'Fri' in days:
            SECTION.meet_fri_start = start
            SECTION.meet_fri_end = end
          if 'Sat' in days:
            SECTION.meet_sat_start = start
            SECTION.meet_sat_end = end
          if 'Sun' in days:
            SECTION.meet_sun_start = start
            SECTION.meet_sun_end = end
          SECTION.save()
          #print "Section created: %s" % SECTION
          _created_section += 1
      except:
        print "ERROR!"
    
    print "Courses:\n  %s Created, %s Updated, %s Skipped" % (
        _created_course, _updated_course, _skipped_course)
    print "Sections:\n  %s Created, %s Updated, %s Skipped" % (
        _created_section, _updated_section, _skipped_section)
  
  def clean(self, c):
    if not c['description']:
      c['description'] = ''
    c['units'] = c['units'].replace('units', '').strip()
    return c
  
