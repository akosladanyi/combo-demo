from django.core.management.base import BaseCommand
from main.models import Client, Network
from time import sleep


class Command(BaseCommand):
    def handle(self, *args, **options):
        net_lst = list(Network.objects.all())
        while True:
            for net in Network.objects.all():
                cl_lst = list(net.client_set.order_by('id').all())
                if len(cl_lst) > 1:
                    sum_spd = 0.0
                    for cl in cl_lst:
                        sum_spd += cl.dl_speed
                    if sum_spd > 3500:
                        cl = cl_lst[0]
                        try:
                            i = net_lst.index(cl.network)
                        except ValueError:
                            continue
                        net = net_lst[(i + 1) % len(net_lst)]
                        cl.network = net
                        cl.save()
                        self.stdout.write('Client {} new network: {}'.format(
                            cl, net))
                        break
            sleep(5)
