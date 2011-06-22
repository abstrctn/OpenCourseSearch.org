from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import redis, base64

from api import helpers
from api.v01_views import course, session, network

def proxy_course(request):
  request.GET = request.GET.copy()
  request.GET['api-key'] = settings.OCS_API_KEY
  return course(request)

def proxy_session(request):
  request.GET = request.GET.copy()
  request.GET['api-key'] = settings.OCS_API_KEY
  return session(request)

def proxy_network(request):
  request.GET = request.GET.copy()
  request.GET['api-key'] = settings.OCS_API_KEY
  return network(request)
