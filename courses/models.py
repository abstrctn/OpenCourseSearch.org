from django.db import models

import datetime

class Note(models.Model):
  text = models.TextField()

class College(models.Model):
  name = models.CharField(max_length=255)
  level = models.CharField(max_length=20)
  
  def __unicode__(self):
    return self.name

class Session(models.Model):
  name = models.CharField(max_length=40)
  start_date = models.DateField()
  end_date = models.DateField()
  
  def __unicode__(self):
    return self.name

class Classification(models.Model):
  college = models.ForeignKey(College, blank=True, null=True)
  
  code = models.CharField(max_length=20)
  name = models.CharField(max_length=100, blank=True)
  
  def __unicode__(self):
    return self.code
  
  class Meta:
    ordering = ('name',)

class Course(models.Model):
  updated_at = models.DateTimeField(default=datetime.datetime.now())
  
  session = models.ForeignKey(Session)
  college = models.ForeignKey(College)
  classification = models.ForeignKey(Classification)
  
  number = models.IntegerField()                  # 200
  
  description = models.TextField(blank=True)
  level = models.CharField(max_length=20)         # Undergraduate
  component = models.CharField(max_length=20)     # Lecture, Recitation
  grading = models.CharField(max_length=20)       # CAS Graded
  location_code = models.CharField(max_length=10) # WS
  course_name = models.CharField(max_length=255)  # Animals & Society
  prof = models.CharField(max_length=100)
  
  def __unicode__(self):
    return "%s-%s" % (self.classification, self.number)
  
  class Meta:
    ordering = ('classification', 'number')

class Section(models.Model):
  updated_at = models.DateTimeField(default=datetime.datetime.now())
  
  course = models.ForeignKey(Course)
  
  is_open = models.BooleanField()                 # Open
  number = models.CharField(max_length=20)
  class_name = models.CharField(max_length=255, blank=True)   # Topics: Animal Minds
  notes = models.TextField(blank=True)        
  #section = models.IntegerField()                 # 001
  section = models.CharField(max_length=10)
  prof = models.CharField(max_length=255)
  units = models.CharField(max_length=10)
  
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
  
  def __unicode__(self):
    return "%s %s" % (self.course, self.section)
  
  class Meta:
    ordering = ('section',)
  
  def get_section(self):
    return str(self.section).rjust(3, "0")
  
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
      return "%s %s" % (start.strftime("%I:%M %p").lstrip('0'), end.strftime("%I:%M %p").lstrip('0'))

