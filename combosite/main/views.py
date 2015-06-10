import json
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from main.models import Client


class GetNetworkView(View):
    def get(self, request, *args, **kwargs):
        client_name = request.GET.get('c')
        try:
            client = Client.objects.get(name=client_name)
        except Client.DoesNotExist:
            return HttpResponseBadRequest('Invalid client.')
        return HttpResponse(json.dumps(client.network.name),
                            content_type='application/json')
