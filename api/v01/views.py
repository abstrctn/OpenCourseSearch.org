from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.template.defaultfilters import slugify

import datetime, json

from haystack.query import SearchQuerySet

from courses.models import *
from networks.models import Network
from api.decorators import api_auth

LIMIT = 20
def course(request):
  data = request.GET
  
  network = data.get('network', '')
  session = slugify(data.get('session', ''))
  query = data.get('query', '')
  offset = int(data.get('offset', 0))
  
#   qs = qs.filter(network = network, session = session)
#   if data.get('college'): # id
#     c = get_object_or_404(College, id=data['college'])
#     qs = qs.filter(college = c)
#   if data.get('subject'): # id
#     c = get_object_or_404(Classification, id=data['subject'])
#     qs = qs.filter(classification = c)
#   if data.get('level'):
#     l = get_object_or_404(Level, id=data['level'])
#     qs = qs.filter(level = l)
#   if data.get('query'):
#     all_txt = data['query']
#     filter_sets = Q(id__gt=0)
#     for txt in all_txt.split(' '):
#       filters = Q(description__icontains=txt) | Q(name__icontains=txt) | Q(classification__name__icontains=txt) | Q(profs__icontains=txt)
#       try:
#         filters = filters | Q(id=int(txt))
#       except: pass
#       filter_sets = filter_sets & filters
#     qs = qs.filter(filter_sets)
#   
#   results = qs[offset:offset+LIMIT]
  
  sqs = SearchQuerySet().models(Course).filter(network=network, session=session).auto_query(query)#.filter_and(network=network, session=session)
  
  
  results = sqs[offset:offset+LIMIT]
  rendered = ",".join([r.json for r in results])
  
  response = {
    'offset': offset,
    'results_per_page': LIMIT,
    'total': sqs.count(),
    'more': ((offset + 1) * LIMIT) < sqs.count(),
    'results': "*****"
  }
  dumped = json.dumps(response)
  dumped = dumped.replace('"*****"', "[%s]" %rendered)
  
  return HttpResponse(dumped, mimetype='application/json')
  #except:
  #  return HttpResponse(status=400)

#@api_auth
def network(request):
  data = request.GET
  network = data.get('network')
  
  all = SearchQuerySet().models(Network)
  sqs = SearchQuerySet().models(Network).filter(slug=network)
  dumped_json = sqs[0].json
  return HttpResponse(dumped_json, mimetype='application/json')

#@api_auth
def session(request):
  data = request.GET
  network = data.get('network', '')
  session = slugify(data.get('session', ''))
  
  dumped_json = SearchQuerySet().models(Session).filter(network=network, slug=session)[0].json
  return HttpResponse(dumped_json, mimetype='application/json')
