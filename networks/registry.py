from django.conf import settings
from courses.models import Session, Network

class NetworkScraper(object):
  def __init__(self, *args, **kwargs):
    self._registry = {} # network slug -> Scraper class
    open(settings.MEDIA_ROOT + 'network_error.log', 'w').close()
  
  def _log_error(self, e):
    f = open(settings.MEDIA_ROOT + 'network_errors.log', 'a')
    f.write('%s' % e)
    f.close()
  
  def registered(self):
    return self._registry.keys()
  
  def get_scraper(self, network_slug):
    return self._registry[network_slug]['scraper']
  
  def get_network(self, network_slug):
    return self._registry[network_slug]['network']
  
  def register(self, network_slug, scraper_model, **kwargs):
    try:
      self._registry[network_slug] = {
        'scraper': scraper_model,
        'network': Network.objects.get(slug=network_slug)
      }
    except Exception, e:
      self._log_error(e)
  
  def run(self, network_slug, session_slug=None):
    for scraper in self._active_scrapers_for_network(network_slug):
      if not session_slug or session_slug == scraper.session.slug:
        print "Running %s scraper: %s" % (network_slug, scraper.session.name)
        scraper.run()
  
  def _active_sessions_for_network(self, network_slug):
    network = Network.objects.get(slug=network_slug)
    return Session.objects.filter(network=network, active=True)
  
  def _active_scrapers_for_network(self, network_slug):
    for session in self._active_sessions_for_network(network_slug):
      yield self._get_scraper_for_session(network_slug, session)
  
  def _get_scraper_for_session(self, network_slug, session):
    scraper_class = self._registry[network_slug]['scraper']
    return scraper_class(debug=True, network=network_slug, session=session)
  
  def _get_or_create_scraper(self, network_slug, **session_attrs):
    network = Network.objects.get(slug=network_slug)
    session, c = Session.objects.get_or_create(
        network=network,
        **session_attrs
    )
    scraper_class = self._registry[network_slug]['scraper']
    scraper = scraper_class(debug=False, network=network_slug, session=session)
    return scraper

network = NetworkScraper()