from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import redis, base64

from api import helpers

def create(request):
  response = helpers.create_subject(request.POST)
  
  return HttpResponse(response)

def register(request):
    return render_to_response('api/register.html', {},
                              context_instance=RequestContext(request))

def register_submit(request):
    email = request.POST['email']
    key = base64.urlsafe_b64encode(email)
    r = redis.Redis(settings.REDIS_HOST)
    if r.get('%s:status' % key):
      msg = "An API key is already assigned to this email address."
      status = 'error'
    else:
      r.set('%s:status' % key, 'pending')
      msg = "Your new API key is: %s" % key
      status = 'success'
    return render_to_response('api/register.html', {'msg': msg, 'status': status},
                              context_instance=RequestContext(request))

