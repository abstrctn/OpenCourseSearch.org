from networks import network
from scrapers.nyu import NYUScraper
from scrapers.unebraska import UNebraskaScraper
from scrapers.osu import OSUScraper
from scrapers.columbia import ColumbiaScraper
from scrapers.ucla import UCLAScraper

network.register('nyu', NYUScraper)
network.register('unl', UNebraskaScraper)
network.register('uno', UNebraskaScraper)
network.register('unk', UNebraskaScraper)
network.register('osu', OSUScraper)
network.register('columbia', ColumbiaScraper)
network.register('ucla', UCLAScraper)