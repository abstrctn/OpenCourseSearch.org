from django.db import models
from django.conf import settings

class Network(models.Model):
  slug = models.SlugField(primary_key=True)
  institution = models.ForeignKey('courses.Institution')
  name = models.CharField(max_length=100)
  abbr = models.CharField(max_length=15)
  active = models.BooleanField()
  default_session = models.ForeignKey('courses.Session', related_name='default_for', null=True, blank=True)
  
  def __unicode__(self):
    return self.name
  
  class Meta:
    ordering = ('name',)

class NetworkManager(models.Manager):
  def get_query_set(self):
    if settings.NETWORK:
      try:
        network = Network.objects.get(slug=settings.NETWORK)
        return super(NetworkManager, self).get_query_set().filter(network=network)
      except: pass
    return super(NetworkManager, self).get_query_set()
