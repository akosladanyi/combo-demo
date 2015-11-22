from django.core.management.base import BaseCommand
from main.models import Client, Network
from time import sleep


class Command(BaseCommand):
    def handle(self, *args, **options):
        net1 = Network.objects.get(pk=1)
        net2 = Network.objects.get(pk=2)
        LIMIT = 2000
        while True:
            clients1 = list(Client.objects.filter(network=net1).order_by('id'))
            clients2 = list(Client.objects.filter(network=net2).order_by('id'))
            cl1 = Client.objects.get(pk=1)
            cl2 = Client.objects.get(pk=2)
            trf1 = 0.0
            trf2 = 0.0
            for cl in clients1:
                trf1 += cl.dl_speed
            for cl in clients2:
                trf2 += cl.dl_speed
            self.stdout.write('{}/{} {}/{}'.format(len(clients1), len(clients2), trf1, trf2))
            # # if len(clients1) > 1 and trf1 > LIMIT and cl2.dl_speed > LIMIT:
            # if len(clients1) > 1 and trf1 > LIMIT:
            #     cl = clients1[0]
            #     cl.network = net2
            #     cl.save()
            #     self.stdout.write('Client {} new network: {}'.format(cl, net2))
            # elif trf1 < LIMIT and len(clients2) > 0:
            #     cl = clients2[0]
            #     cl.network = net1
            #     cl.save()
            #     self.stdout.write('Client {} new network: {}'.format(cl, net1))
            if cl1.network == net1 and cl2.network == net1 and cl2.dl_speed > LIMIT:
                cl1.network = net2
                cl1.save()
                self.stdout.write('Client {} new network: {}'.format(cl1, net2))
            elif cl1.network == net2 and cl2.network == net2 and cl2.dl_speed > LIMIT:
                cl1.network = net1
                cl1.save()
                self.stdout.write('Client {} new network: {}'.format(cl1, net1))
            elif cl1.network == net1 and cl2.network == net2 and cl2.dl_speed < LIMIT:
                cl1.network = net2
                cl1.save()
                self.stdout.write('Client {} new network: {}'.format(cl1, net2))
            elif cl1.network == net2 and cl2.network == net1 and cl2.dl_speed < LIMIT:
                cl1.network = net1
                cl1.save()
                self.stdout.write('Client {} new network: {}'.format(cl1, net1))

            sleep(5)
