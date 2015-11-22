import json
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from main.models import Client, Network


class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        ns = Network.objects.order_by('name').prefetch_related('client_set')
        context['networks'] = ns
        return context


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


class GetConnectedClientsView(View):
    def get(self, request, *args, **kwargs):
        ns = Network.objects.order_by('name').prefetch_related('client_set')
        lst = []
        for n in ns:
            dct = {
                'network_id': n.id,
                'network_name': n.name,
                'clients': [],
            }
            for c in n.client_set.order_by('name'):
                dct2 = {
                    'client_id': c.id,
                    'client_name': c.name,
                    'ul_speed': c.ul_speed,
                    'dl_speed': c.dl_speed,
                }
                dct['clients'].append(dct2)
            lst.append(dct)
        return HttpResponse(json.dumps(lst), content_type='application/json')
