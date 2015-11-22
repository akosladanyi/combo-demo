from django.contrib import admin
from main.models import Network, Client


class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'network']


admin.site.register(Network)
admin.site.register(Client, ClientAdmin)
