from django.http import Http404
from django.views.generic import date_based, list_detail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from datetime import datetime
from django.db.models import Q
from django.core.paginator import Paginator

from courses.models import *

def search(request):
    colleges = College.objects.all()
    subjects = Classification.objects.all()
    total_courses = Course.objects.all().count()
    total_sections = Section.objects.all().count()
    
    return render_to_response('search.html',
                              {'colleges': colleges,
                               'subjects': subjects,
                               'total_courses': total_courses,
                               'total_sections': total_sections,},
                              context_instance=RequestContext(request))

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
                              {'sections': sections, 'undo': undo},
                              context_instance=RequestContext(request))
    

def results(request):
    data = request.GET
    qs = Course.objects.all()
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
      txt = data['text']
      filters = Q(description__icontains=txt) | Q(course_name__icontains=txt) | Q(classification__name__icontains=txt)
      try:
        filters = filters | Q(id=int(txt))
      except: pass
      qs = qs.filter(filters)
    
    #if not (data.get('text', '') or data.get('level', '') or data.get('college', '') or data.get('subject', '')):
    #  qs = []
    
    pg = data.get('page', 1)
    p = Paginator(qs, 20)
    page = p.page(pg)
    
    results = page.object_list
    return render_to_response('results.html',
                              {'results': results, 'page': page},
                              context_instance=RequestContext(request))

