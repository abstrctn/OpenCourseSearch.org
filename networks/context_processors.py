from django.conf import settings # import the settings file
from networks.models import Network
from courses.models import Course, Section

def network(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    
    if settings.NETWORK in ['home', 'none', '']:
      n = {'slug': 'home'}
      institution = None
    else:
      n = Network.objects.get(slug=settings.NETWORK)
      institution = n.institution
    return {
      'NETWORK': n,
      'INSTITUTION': institution,
      'total_courses': Course.objects.all().count(),
      'total_sections': Section.objects.all().count()
    }
