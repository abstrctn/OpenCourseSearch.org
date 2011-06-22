import pickle, re, os
from courses.models import *
from django.conf import settings

def load_listing(key):
  f = open('%s%s.txt' % (settings.MEDIA_ROOT, key))
  data = pickle.load(f)
  SESSION, created = Session.objects.get_or_create(name='Fall 2011',
      start_date=datetime.datetime(2011,9,6),
      end_date=datetime.datetime(2011,12,16))
  
  _created_course = 0
  _updated_course = 0
  _skipped_course = 0
  _created_section = 0
  _updated_section = 0
  _skipped_section = 0
  for id in data.keys():
    try:
      c = data[id]
      c = clean(c)
      start, end = None, None
      
      number = c['number']
      try:
        CLASSIFICATION, created = Classification.objects.get_or_create(code=c['classification'])
      except:
        CLASSIFICATION = Classification.objects.filter(code=['classification'])[0]
      COLLEGE, created = College.objects.get_or_create(name=c['college'])
      
      # parse meet data
      meet = c['meet_data']
      meet = meet.replace('09/06/2011 - 12/23/2011 ', '')
      try:
        days = re.search('(([A-Z][a-z][a-z],?){1,3})', meet).groups()[0].split(',')
      except: days = []
      try:
        start, end = re.search('(\d{1,2}\.\d{2} \w{2})[^\d]*(\d{1,2}\.\d{2} \w{2})', meet).groups()
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
        prof = re.search('with (.*)', meet).groups()[0]
      except:
        prof = ''
      
      # get or create the course
      qs = Course.objects.filter(
      
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
          session = SESSION,
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
      #qs = Section.objects.filter(course = COURSE, section = c['section'])
      qs = Section.objects.filter(number = id)
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
        if c['prof'] and c['prof'] != SECTION.prof:
          SECTION.prof = c['prof']
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
          course = COURSE,
          is_open = c['is_open'],
          class_name = c['class_name'],
          notes = c['notes'],
          section = c['section'],
          prof = c['prof'],
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
    except Exception, e:
      print "ERROR!: %s" % e
  
  print "Courses:\n  %s Created, %s Updated, %s Skipped" % (
      _created_course, _updated_course, _skipped_course)
  print "Sections:\n  %s Created, %s Updated, %s Skipped" % (
      _created_section, _updated_section, _skipped_section)

def load_all_listings():
  from courses.helpers import *
  for f in os.listdir(settings.MEDIA_ROOT):
    try:
      t = re.search('(LINK\d\$\d{1,3}).txt', f).groups()[0]
      load_listing(t)
    except Exception, e:
      print e


def clean(c):
  if not c['description']:
    c['description'] = ''
  c['units'] = c['units'].replace('units', '').strip()
  return c

def load_classifications():
  #f = open('/opt/django-projects/ocs/storage/classifications.txt')
  f = open('%scollege-classifications.txt' % (settings.MEDIA_ROOT))
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
  