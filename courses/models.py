from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify

import datetime, itertools

from networks.models import Network, NetworkManager

class Institution(models.Model):
  slug = models.CharField(max_length=20)
  name = models.CharField(max_length=200)
  
  def __unicode__(self):
    return self.name
    
class College(models.Model):
  network = models.ForeignKey(Network, null=True, blank=True)
  institution = models.ForeignKey(Institution, null=True, blank=True)
  name = models.CharField(max_length=255)
  slug = models.SlugField()
  short_name = models.CharField(max_length=255)
  #level = models.CharField(max_length=20)
  
  objects = NetworkManager()
  
  def __unicode__(self):
    return self.name
  
  class Meta:
    ordering = ('id',)
  
  def save(self, *args, **kwargs):
    if self.name:
      self.slug = slugify(self.name)[:60]
    super(College, self).save(*args, **kwargs)
  
  def get_short_name(self):
    if self.short_name:
      return self.short_name
    return self.name

class Session(models.Model):
  network = models.ForeignKey(Network)
  classifications = models.ManyToManyField('Classification', blank=True)
  colleges = models.ManyToManyField('College', blank=True)
  levels = models.ManyToManyField('Level', blank=True)
  
  name = models.CharField(max_length=40)
  slug = models.SlugField()
  system_code = models.CharField(max_length=20, null=True, blank=True)
  start_date = models.DateField()
  end_date = models.DateField()
  
  active = models.BooleanField(default=False)
  
  objects = NetworkManager()
  
  def __unicode__(self):
    return "%s: %s" % (self.network, self.name)
  
  @models.permalink
  def get_absolute_url(self):
    return ('networks.views.session_home', (), {
      'session_slug': self.slug,
    })

class SessionInfo(models.Model):
  session = models.ForeignKey(Session)
  info_type = models.CharField(max_length=100)
  info_value = models.CharField(max_length=100)

class Classification(models.Model):
  network = models.ForeignKey(Network)
  institution = models.ForeignKey(Institution)
  college = models.ForeignKey(College, blank=True, null=True)
  
  code = models.CharField(max_length=20)
  name = models.CharField(max_length=100, blank=True)
  slug = models.SlugField()
  
  objects = NetworkManager()
  
  def __unicode__(self):
    return self.code
  
  class Meta:
    ordering = ('name',)
  
  def save(self, *args, **kwargs):
    if self.name:
      self.slug = slugify(self.name)[:60]
    super(Classification, self).save(*args, **kwargs)
  
  def get_level(self):
    if self.code[-2] == 'U':
      return "Undergraduate"
    elif self.code[-2] in ['G', 'D']:
      return "Graduate"
    elif self.code[-2] == 'A':
      return "NYUAD"
    return

class Level(models.Model):
  network = models.ForeignKey(Network, null=True, blank=True)
  institution = models.ForeignKey(Institution)
  name = models.CharField(max_length=50)
  slug = models.SlugField()
  
  def __unicode__(self):
    return self.name
  
  def save(self, *args, **kwargs):
    if self.name:
      self.slug = slugify(self.name)[:60]
    super(Level, self).save(*args, **kwargs)

class Course(models.Model):
  updated_at = models.DateTimeField(default=datetime.datetime.now())
  
  network = models.ForeignKey(Network, null=True, blank=True)
  institution = models.ForeignKey(Institution, null=True, blank=True)
  college = models.ForeignKey(College, null=True, blank=True)
  classification = models.ForeignKey(Classification, null=True, blank=True)
  session = models.ForeignKey(Session)
  
  number = models.CharField(max_length=10)
  
  description = models.TextField(blank=True)
  grading = models.CharField(max_length=50)       # CAS Graded
  #location_code = models.CharField(max_length=10) # WS
  name = models.CharField(max_length=255)  # Animals & Society
  slug = models.SlugField()
  profs = models.TextField()
  level = models.ForeignKey(Level, null=True, blank=True)
  
  objects = NetworkManager()
  
  def __unicode__(self):
    return "%s (%s-%s)" % (self.name, self.classification, self.number)
  
  class Meta:
    ordering = ('classification', 'number')
  
  def save(self, *args, **kwargs):
    sections = self.sections.all()
    profs = [s.prof for s in sections]
    self.profs = " ".join(profs)
    if self.name:
      self.slug = slugify(self.name)[:60]
    return super(Course, self).save(*args, **kwargs)
  
  @models.permalink
  def get_absolute_url(self):
    slugs = "/".join(filter(None, [self.classification.slug, self.slug, "-".join([self.classification.code, self.number])]))
    return ('course_detail', (), {
      'session_slug': self.session.slug,
      'slugs': slugs
    })

ORDERED_DAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'TBA', '')
class Section(models.Model):
  updated_at = models.DateTimeField(default=datetime.datetime.now())
  
  network = models.ForeignKey(Network, null=True, blank=True)
  institution = models.ForeignKey(Institution, blank=True, null=True)
  course = models.ForeignKey(Course, related_name='sections')
  
  status = models.CharField(max_length=20)
  
  number = models.CharField(max_length=20)
  name = models.CharField(max_length=255, blank=True)   # Topics: Animal Minds
  notes = models.TextField(blank=True)
  #section = models.IntegerField()                 # 001
  #section = models.CharField(max_length=10)
  prof = models.CharField(max_length=255)
  units = models.CharField(max_length=10)
  component = models.CharField(max_length=20)     # Lecture, Recitation
  reference_code = models.CharField(max_length=10, blank=True) # school's internal id for class
  
  seats_capacity = models.IntegerField(blank=True, null=True)
  seats_taken = models.IntegerField(blank=True, null=True)
  seats_available = models.IntegerField(blank=True, null=True)
  waitlist_capacity = models.IntegerField(blank=True, null=True)
  waitlist_taken = models.IntegerField(blank=True, null=True)
  waitlist_available = models.IntegerField(blank=True, null=True)
  
  # moved to meeting
  location = models.CharField(max_length=100)
  room = models.CharField(max_length=20)
  
  # could partition into fk, but being safe for speed at launch
  meet_mon_start = models.TimeField(blank=True, null=True)
  meet_mon_end = models.TimeField(blank=True, null=True)
  meet_tue_start = models.TimeField(blank=True, null=True)
  meet_tue_end = models.TimeField(blank=True, null=True)
  meet_wed_start = models.TimeField(blank=True, null=True)
  meet_wed_end = models.TimeField(blank=True, null=True)
  meet_thu_start = models.TimeField(blank=True, null=True)
  meet_thu_end = models.TimeField(blank=True, null=True)
  meet_fri_start = models.TimeField(blank=True, null=True)
  meet_fri_end = models.TimeField(blank=True, null=True)
  meet_sat_start = models.TimeField(blank=True, null=True)
  meet_sat_end = models.TimeField(blank=True, null=True)
  meet_sun_start = models.TimeField(blank=True, null=True)
  meet_sun_end = models.TimeField(blank=True, null=True)
  
  objects = NetworkManager()
  
  def __unicode__(self):
    return "%s .%s" % (self.course, self.number)
  
  class Meta:
    ordering = ('course','number')
  
  def get_number(self):
    return str(self.number).rjust(3, "0")
  
  def grouped_meetings(self):
    meetings = self.meeting_set.all()
    try:
      sorted_meetings = sorted(meetings, key=lambda x: ORDERED_DAYS.index(x.day))#sorted(meetings, key=lambda x: [x.start, x.end, x.location, x.room])
      grouper = itertools.groupby(sorted_meetings, key=lambda x: [x.start, x.end, x.location, x.room])
      m = []
      for key, groups in grouper:
        m.append(list(groups))
      return m
    except: return [meetings]
  
  def get_profs(self):
    return self.prof.split(', ')
  
  """
  def days(self):
    ret = []
    if self.meet_mon_start:
      ret.append('Mon')
    if self.meet_tue_start:
      ret.append('Tue')
    if self.meet_wed_start:
      ret.append('Wed')
    if self.meet_thu_start:
      ret.append('Thu')
    if self.meet_fri_start:
      ret.append('Fri')
    if self.meet_sat_start:
      ret.append('Sat')
    if self.meet_sun_start:
      ret.append('Sun')
    return ", ".join(ret)
  
  def times(self):
    ret = []
    start = ''
    end = ''
    if self.meet_mon_start:
      start = self.meet_mon_start
    if self.meet_tue_start:
      start = self.meet_tue_start
    if self.meet_wed_start:
      start = self.meet_wed_start
    if self.meet_thu_start:
      start = self.meet_thu_start
    if self.meet_fri_start:
      start = self.meet_fri_start
    if self.meet_sat_start:
      start = self.meet_sat_start
    if self.meet_sun_start:
      start = self.meet_sun_start
    
    if self.meet_mon_end:
      end = self.meet_mon_end
    if self.meet_tue_end:
      end = self.meet_tue_end
    if self.meet_wed_end:
      end = self.meet_wed_end
    if self.meet_thu_end:
      end = self.meet_thu_end
    if self.meet_fri_end:
      end = self.meet_fri_end
    if self.meet_sat_end:
      end = self.meet_sat_end
    if self.meet_sun_end:
      end = self.meet_sun_end
    
    if start and end:
      return "%s  -  %s" % (start.strftime("%I:%M %p").lstrip('0'), end.strftime("%I:%M %p").lstrip('0'))
  """

DAY_CHOICES = (
  ('Mon', 'Mon'),
  ('Tue', 'Tue'),
  ('Wed', 'Wed'),
  ('Thu', 'Thu'),
  ('Fri', 'Fri'),
  ('Sat', 'Sat'),
  ('Sun', 'Sun'),
)
class Meeting(models.Model):
  section = models.ForeignKey(Section)
  day = models.CharField(max_length=3, choices=DAY_CHOICES)
  start = models.TimeField(blank=True, null=True)
  end = models.TimeField(blank=True, null=True)
  location = models.CharField(max_length=100)
  room = models.CharField(max_length=20)
  
  def __unicode__(self):
    return "%s: %s - %s" % (self.day, self.start, self.end)
