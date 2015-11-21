import json
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
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


class SetSpeedView(View):
    def get(self, request, *args, **kwargs):
        client_name = request.GET.get('c')
        try:
            client = Client.objects.get(name=client_name)
        except Client.DoesNotExist:
            return HttpResponseBadRequest('Invalid client.')
        client.ul_speed = float(request.GET.get('ul'))
        client.dl_speed = float(request.GET.get('dl'))
        client.save()
        return HttpResponse()
