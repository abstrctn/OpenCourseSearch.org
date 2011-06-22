from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.serializers import serialize

import datetime, json

from haystack.query import SearchQuerySet

from courses.models import *
from networks.models import Network
from api.decorators import api_auth

LIMIT = 20
def course(request):
  data = request.GET
  qs = Course.objects.all()
  #try:
  
  network = get_object_or_404(Network, slug=data.get('network'))
  session = get_object_or_404(Session, network=network, slug=data['session'])
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
  
  results = SearchQuerySet().models(Course).all()[offset:offset+LIMIT]
  rendered = ",".join([r.json for r in results])
  
  response = {
    'offset': offset,
    'results_per_page': LIMIT,
    'total': qs.count(),
    'more': ((offset + 1) * LIMIT) < qs.count(),
    'results': "*****"
  }
  dumped = json.dumps(response)
  dumped = dumped.replace('"*****"', "[%s]" %rendered)
  
  return HttpResponse(dumped, mimetype='application/json')
  #except:
  #  return HttpResponse(status=400)

@api_auth
def network(request):
  data = request.GET
  network = get_object_or_404(Network, slug=data['network'])
  
  response = {
    'slug': network.slug,
    'name': network.name,
    'abbr': network.abbr,
    'sessions': [
      {
        'slug': session.slug,
        'name': session.name,
        'start_date': session.start_date.strftime('%Y-%m-%d'),
        'end_date': session.end_date.strftime('%Y-%m-%d'),
        'code': session.system_code,
        'id': session.id,
        'default': network.default_session == session
      } for session in network.session_set.all()
    ]
  }
  return HttpResponse(json.dumps(response), mimetype='application/json')

@api_auth
def session(request):
  data = request.GET
  network = get_object_or_404(Network, slug=data['network'])
  session = get_object_or_404(Session, network=network, slug=data['session'])
  
  response = {
    'slug': session.slug,
    'name': session.name,
    'start_date': session.start_date.strftime('%Y-%m-%d'),
    'end_date': session.end_date.strftime('%Y-%m-%d'),
    'code': session.system_code,
    'id': session.id,
    'colleges': [
      {
        'slug': college.slug,
        'name': college.name,
        'short_name': college.short_name,
        'id': college.id
      } for college in session.colleges.all()
    ],
    'subjects': [
      {
        'code': classification.code,
        'name': classification.name,
        'slug': classification.slug,
        'id': classification.id,
        'college': classification.college.id if classification.college else None,
      } for classification in session.classifications.all()
    ],
    'levels': [
      {
        'name': level.name,
        'slug': level.slug,
        'id': level.id
      } for level in session.levels.all()
    ],
  }
  return HttpResponse(json.dumps(response), mimetype='application/json')




"""
LIMIT = 20
@api_auth
def course(request):
  data = request.GET
  qs = Course.objects.all()
  #try:
  
  network = get_object_or_404(Network, slug=data.get('network'))
  session = get_object_or_404(Session, network=network, slug=data['session'])
  offset = int(data.get('offset', 0))
  
  qs = qs.filter(network = network, session = session)
  if data.get('college'): # id
    c = get_object_or_404(College, id=data['college'])
    qs = qs.filter(college = c)
  if data.get('subject'): # id
    c = get_object_or_404(Classification, id=data['subject'])
    qs = qs.filter(classification = c)
  if data.get('level'):
    l = get_object_or_404(Level, id=data['level'])
    qs = qs.filter(level = l)
  if data.get('query'):
    all_txt = data['query']
    filter_sets = Q(id__gt=0)
    for txt in all_txt.split(' '):
      filters = Q(description__icontains=txt) | Q(name__icontains=txt) | Q(classification__name__icontains=txt) | Q(profs__icontains=txt)
      try:
        filters = filters | Q(id=int(txt))
      except: pass
      filter_sets = filter_sets & filters
    qs = qs.filter(filter_sets)
  
  results = qs[offset:offset+LIMIT]
  
  response = {
    'offset': offset,
    'results_per_page': LIMIT,
    'total': qs.count(),
    'more': ((offset + 1) * LIMIT) < qs.count(),
    'results': [
      {
        'name': result.name,
        'id': result.id,
        'number': result.number,
        'classification': {
          'code': result.classification.code,
          'name': result.classification.name,
          'college': {
            'name': result.college.name,
            'slug': result.college.slug,
          } if result.college else None
        },
        'level': result.level.name if result.level else None,
        'grading': result.grading,
        'description': result.description,
        'sections': [
          {
            'id': section.id,
            'reference_code': section.reference_code,
            'number': section.number,
            'name': section.name,
            'status': {
              'label': section.status,
              'seats': {
                'total': section.seats_capacity,
                'taken': section.seats_taken,
                'available': section.seats_available
              } if section.seats_taken else None,
              'waitlist': {
                'total': section.waitlist_capacity,
                'taken': section.waitlist_taken,
                'available': section.waitlist_available
              } if section.waitlist_capacity or section.waitlist_taken else None
            },
            'component': section.component,
            'prof': section.prof,
            'units': section.units,
            'notes': section.notes,
            'meets': [
              {
                'day': ", ".join([meeting.get_day_display() for meeting in meetings]),
                'start': meetings[0].start.strftime('%I:%M %p') if meetings and meetings[0].start else None,
                'end': meetings[0].end.strftime('%I:%M %p') if meetings and meetings[0].end else None,
                'location': meetings[0].location if meetings else None,
                'room': meetings[0].room if meetings else None,
              } for meetings in section.grouped_meetings()
            ]
          } for section in result.sections.all()
        ],
      } for result in results
    ],
  }
  
  return HttpResponse(json.dumps(response), mimetype='application/json')
  #except:
  #  return HttpResponse(status=400)
"""