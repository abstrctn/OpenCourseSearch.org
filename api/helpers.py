import datetime, re

from django.http import HttpResponse
from django.template.defaultfilters import slugify

from courses.models import *
from networks.models import Network

def create_section(data):
  network = Network.objects.get(slug = data['network'])
  institution = Institution.objects.get(slug = data['institution'])
  session = Session.objects.get(id=data['session'])
  
  if data.get('college'):
    college, created = College.objects.get_or_create(
      institution = institution,
      network = network,
      name = clean(data['college'])
    )
    session.colleges.add(college)
  else:
    college = None

  classification, created = Classification.objects.get_or_create(
    code = data['classification'],
    college = college,
    name = clean(data['classification_name']),
    institution = institution,
    network = network,
  )
  session.classifications.add(classification)
  
  if data.get('level'):
    level, created = Level.objects.get_or_create(
      name = clean(data['level']),
      slug = slugify(clean(data['level'])),
      institution = institution,
      network = network,
    )
    session.levels.add(level)
  else:
    level = None
  
  # get or create the course
  course, course_created = Course.objects.get_or_create(
    network = network,
    institution = institution,
    classification = classification,
    number = data['number'],
    session = session,
    college = college,
    level = level,
  )

  course, updated = update_attrs(course, {
    'session': session,
    #'location_code': data['loc_code'],
    'name': data['course_name'],
    'description': data['description'],
    'grading': data['grading'][:50],
  })
  course.save()
  
  # get or create the section
  section, section_created = Section.objects.get_or_create(
    network = network,
    reference_code=data['reference_code'],
    institution=institution,
    course=course
  )
  section_attrs = {
    'institution': institution,
    'course': course,
    'number': data['section'],
    'status': data['status'],
    'name': data.get('section_name', ''),
    'notes': data.get('notes', ''),
    'prof': data['prof'],
    'units': data['units'],
    'component': data['component'][:20],
    #'location': data.get('location', ''),
    #'room': data.get('room', ''),
    'seats_capacity': data.get('seats_capacity', None),
    'seats_taken': data.get('seats_taken', None),
    'seats_available': data.get('seats_available', None),
    'waitlist_capacity': data.get('waitlist_capacity', None),
    'waitlist_taken': data.get('waitlist_taken', None),
    'waitlist_available': data.get('waitlist_available', None),
  }
  
  """
  for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
    if day in data.get('days', []):
      if data.get('start_time'):
        section_attrs['meet_%s_start' % day.lower()] = datetime.datetime.strptime(data['start_time'], "%H:%M").time()
      if data.get('end_time'):
        section_attrs['meet_%s_end' % day.lower()] = datetime.datetime.strptime(data['end_time'], "%H:%M").time()
  """
  
  section, updated = update_attrs(section, section_attrs, force_insert=True)
  section.save()
  
  for m in data.get('meetings', []):
    if len(m.get('day', '')) == 1:
      day = {'M': 'Mon', 'T': 'Tue', 'W': 'Wed', 'R': 'Thu', 'F': 'Fri', 'S': 'Sat', 'U': 'Sun', '': ''}[m.get('day', '')]
    else: day = m.get('day')
    meeting, created = Meeting.objects.get_or_create(section=section, day=day)
    meeting_attrs = {
      'start': m.get('start', None),
      'end': m.get('end', None),
      'location': m.get('location', None),
      'room': m.get('room', None),
    }
    print meeting_attrs
    update_attrs(meeting, meeting_attrs, force_insert=True)
    meeting.save()
  
  course.save() # update derived params
  
  #print "Course: %s, Section: %s" % (course_created, section_created)
  response = 'success'
  return response

def update_attrs(obj, attrs, force_insert=False):
  updated = False
  for field in attrs.keys():
    pre_save = getattr(obj, field)
    cleaned = clean(attrs[field])
    if force_insert or cleaned:
      setattr(obj, field, clean(attrs[field]))
    if pre_save != getattr(obj, field):
      updated = True
  return obj, updated

REPLACEMENTS = [
  ('&#039;', "'"),
  ('<br />', ''),
  ('&nbsp;', ' '),
  ('&quot;', '"'),
  ('&amp;', '&'),
]
def clean(attr):
  if type(attr) in [str, unicode]:
    if re.match('\d{2}:\d{2}', attr): # time
      return datetime.datetime.strptime(attr, "%H:%M").time()
    for key, value in REPLACEMENTS:
      attr = attr.replace(key, value)
    attr = attr.strip()
    if attr in ["None", "none"]:
      attr = ''
  return attr
