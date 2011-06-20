from django.contrib import admin
from networks.models import Network

class NetworkAdmin(admin.ModelAdmin):
  pass

admin.site.register(Network, NetworkAdmin)
