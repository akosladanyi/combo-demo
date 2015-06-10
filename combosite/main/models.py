from django.db import models
from django.utils.translation import ugettext_lazy as _


class Network(models.Model):
    name = models.CharField(_('name'), max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('network')
        verbose_name_plural = _('networks')


class Client(models.Model):
    name = models.CharField(_('name'), max_length=128, unique=True)
    mac_address = models.CharField(_('MAC address'), max_length=17, unique=True)
    network = models.ForeignKey(Network, verbose_name=_('network'), blank=True,
                                null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
