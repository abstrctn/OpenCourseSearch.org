from django.http import HttpResponse
from django.conf import settings
import functools, redis

def api_auth(method):
  @functools.wraps(method)
  def wrapper(request, *args, **kwargs):
    key = request.GET.get('api-key', '')
    r = redis.Redis(settings.REDIS_HOST)
    state = r.get('%s:status' % key)
    if state in ['pending', 'active']:
      r.incr('%s:requests' % key)
      return method(request, *args, **kwargs)
    elif state in ['inactive', '']:
     return HttpResponse('403 Developer Inactive', status=403)
    else:
     return HttpResponse('403 Developer Inactive', status=403)
      
  return wrapper
