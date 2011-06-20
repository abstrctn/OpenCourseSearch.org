from django.http import Http404
from django.conf import settings
from django.views.generic import date_based, list_detail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Q
from django.core.paginator import Paginator

import math
from datetime import datetime

from courses.models import *
def inbox(request, action):
    try:
      request.session['inbox'].keys()
    except:
      request.session['inbox'] = {}
    inb = request.session['inbox']
    undo = None
    
    if request.GET.get('id', None):
      id = request.GET['id']
      section = get_object_or_404(Section, id=id)
      
      if action == 'add':
        inb[id] = True
      elif action == 'remove':
        try:
          del inb[id]
          undo = id
        except: pass
    
    request.session['inbox'] = inb
    sections = Section.objects.filter(id__in=inb.keys())
    return render_to_response('inbox.html',
                              {'sections': sections,
                               'undo': undo,
                               'total_courses': Course.objects.all().count(),
                               'total_sections': Section.objects.all().count(),
                               },
                              context_instance=RequestContext(request))

def stats_search(request):
    # open / closed overview
    # each box stands for 20 courses
    data = request.GET
    crumbs = []
    qs = Section.objects.all()
    if data.get('institution', ''):
      i = Institution.objects.get(slug=data['institution'])
      qs = qs.filter(institution = i)
    if data.get('session', ''):
      s = Session.objects.get(slug=data['session'])
      qs = qs.filter(course__session = s)
    if data.get('college', ''):
      c = get_object_or_404(College, id=data['college'])
      qs = qs.filter(course__college = c)
      crumbs.append("%s" % c)
    if data.get('subject', ''):
      c = get_object_or_404(Classification, id=data['subject'])
      qs = qs.filter(course__classification = c)
      crumbs.append("%s" % c.name)
    
    availability = {
      'open': {'count': qs.filter(status='Open').count()},
      'wait': {'count': qs.filter(status='Wait List').count()},
      'closed': {'count': qs.filter(status='Closed').count()},
      'unknown': {'count': qs.filter(status='').count()},
      'boxes': [],
    }
    
    MAX_BOXES = 600
    BOX_VALUE = max(5, qs.count() / MAX_BOXES)
    BOX_VALUE = min(600, BOX_VALUE)
    availability['box_value'] = BOX_VALUE
    
    for key in ['open', 'wait', 'closed', 'unknown']:
      availability[key]['box_count'] = math.ceil(availability[key]['count'] / float(BOX_VALUE))
      availability[key]['percentage'] = availability[key]['count'] / float(qs.count()) * 100
      availability['boxes'].extend([key for i in range(0, availability[key]['box_count'])])
    
    return render_to_response('stats.html',
                              {'availability': availability,
                               'crumbs': " > ".join(crumbs),
                               'total_results': qs.count(),
                               'total_courses': Course.objects.all().count(),
                               'total_sections': Section.objects.all().count(),
                              },
                              context_instance=RequestContext(request))

# Deprecated
"""
def results(request):
    data = request.GET
    qs = Course.objects.all()
    if data.get('institution', ''):
      i = Institution.objects.get(slug = data['institution'])
      qs = qs.filter(institution = i)
    if data.get('level', ''):
      m = {'U': 'Undergraduate', 'G': 'Graduate'}
      qs = qs.filter(level = m[data['level']])
    if data.get('college', ''):
      c = get_object_or_404(College, id=data['college'])
      qs = qs.filter(college = c)
    if data.get('subject', ''):
      c = get_object_or_404(Classification, id=data['subject'])
      qs = qs.filter(classification = c)
    if data.get('text', ''):
      all_txt = data['text']
      filter_sets = Q(id__gt=0)
      for txt in all_txt.split(' '):
        filters = Q(description__icontains=txt) | Q(name__icontains=txt) | Q(classification__name__icontains=txt) | Q(profs__icontains=txt)
        try:
          filters = filters | Q(id=int(txt))
        except: pass
        filter_sets = filter_sets & filters
      qs = qs.filter(filter_sets)
    
    pg = data.get('page', 1)
    p = Paginator(qs, 20)
    page = p.page(pg)
    
    f = open(settings.MEDIA_ROOT + 'searches.log', 'a')
    f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (data.get('level'), data.get('college'), data.get('subject'), pg, '1', data.get('text')))
    f.close()
    
    results = page.object_list
    return render_to_response('results.html',
                              {'results': results,
                               'page': page,
                               'total_courses': Course.objects.all().count(),
                               'total_sections': Section.objects.all().count(),
                               },
                              context_instance=RequestContext(request))

def stats_home(request):
    colleges = College.objects.all()
    subjects = Classification.objects.all()
    
    return render_to_response('stats_home.html',
                              {'colleges': colleges,
                               'subjects': subjects,
                               'total_courses': Course.objects.all().count(),
                               'total_sections': Section.objects.all().count(),
                               },
                              context_instance=RequestContext(request))


def search(request):
    colleges = College.objects.all()
    subjects = Classification.objects.all()
    
    return render_to_response('search.html',
                              {'colleges': colleges,
                               'subjects': subjects,
                               'total_courses': Course.objects.all().count(),
                               'total_sections': Section.objects.all().count(),
                               },
                              context_instance=RequestContext(request))

"""