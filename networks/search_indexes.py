import json

from haystack.indexes import *
from haystack import site

from networks.models import Network
class NetworkIndex(RealTimeSearchIndex):
  text = CharField(document=True, use_template=True)
  json = CharField(indexed=False)
  
  slug = CharField(model_attr='slug')
  
  def index_queryset(self):
    return Network.objects.all()
  
  def prepare_slug(self, obj):
    return obj.slug
  
  def prepare_json(self, obj):
    data = {
      'slug': obj.slug,
      'name': obj.name,
      'abbr': obj.abbr,
      'sessions': [
        {
          'slug': session.slug,
          'name': session.name,
          'start_date': session.start_date.strftime('%Y-%m-%d'),
          'end_date': session.end_date.strftime('%Y-%m-%d'),
          'code': session.system_code,
          'id': session.id,
          'default': obj.default_session == session
        } for session in obj.session_set.all()
      ]
    }
    return json.dumps(data)
site.register(Network, NetworkIndex)