from django.http import Http404
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from courses.models import *

def index(request):
  networks = Network.objects.filter(active=True)
  return render_to_response('network/index.html',
                            {'networks': networks,
                             'total_courses': Course.objects.all().count(),
                             'total_sections': Section.objects.all().count()},
                            context_instance=RequestContext(request))

def session_home(request, session_slug=None):
  if not session_slug:
    session = Network.objects.get(slug=settings.NETWORK).default_session
  else:
    session = get_object_or_404(Session, slug=session_slug)
  
  return render_to_response('network/session.html',
                            {'total_courses': Course.objects.filter(session=session).count(),
                             'total_sections': Section.objects.filter(course__session=session).count(),
                             'session': session,
                             },
                            context_instance=RequestContext(request))

def course(request, session_slug, slugs):
  session = get_object_or_404(Session, slug=session_slug)
  
  # /fall-2011/journalism/senior-seminar/JOUR-UA-401/
  bits = filter(None, slugs.split("/"))
  classif_code, number = bits[-1].rsplit('-', 1)
  classification = get_object_or_404(Classification, code=classif_code)
  course = get_object_or_404(Course, session=session, classification=classification, number=number)
  
  slug_path = []
  slug_path.extend([course.classification.slug, course.slug])
  
  if bits[:-1] != slug_path:
    return Http404()
  return render_to_response('network/course.html', {'course': course, 'session': session},
          context_instance=RequestContext(request))
  
