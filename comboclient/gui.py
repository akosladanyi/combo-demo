#!/usr/bin/python3
from gi.repository import Gtk
import json
import subprocess


class Interface:
    def __init__(self, id, **kwargs):
        self.id = id
        self.is_up = False
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.device


class Network:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.name


class MyListBoxRow(Gtk.ListBoxRow):
    def __init__(self, iface, networks, sel_idx, window):
        Gtk.ListBoxRow.__init__(self)

        self.interface = iface 
        self.networks = networks
        self.window = window
        self.curr_network = None

        self.lbl = Gtk.Label(label='{} ({})'.format(iface.type, iface.device),
                             xalign=0)

        self.cb = Gtk.CheckButton()
        self.cb.set_label('Default route')
        self.cb.connect('toggled', self.on_default_route_toggled)
        self.cb.set_sensitive(False)

        self.sw = Gtk.Switch()
        self.sw.connect('notify::active', self.on_switch_activated, iface)
        self.sw.set_active(False)

        self.cbt = Gtk.ComboBoxText()
        self.cbt.connect('changed', self.on_network_changed)
        if len(self.networks) > 0:
            for net in self.networks:
                self.cbt.append_text(net.name)
            self.cbt.set_active(sel_idx)

        self.box = Gtk.Box(spacing=6)
        self.box.pack_start(self.lbl, True, True, 0)
        self.box.pack_start(self.cbt, False, False, 0)
        self.box.pack_start(self.cb, False, False, 0)
        self.box.pack_start(self.sw, False, False, 0)
        self.add(self.box)

    def on_network_changed(self, combo):
        text = combo.get_active_text()
        if text is None:
            self.curr_network = None
        else:
            for net in self.networks:
                if net.name == text:
                    self.curr_network = net
                    break
            else:
                self.curr_network = None
        print('current network', self.curr_network)

    def on_default_route_toggled(self, button):
        if button.get_active():
            if self.window.default_route is not None:
                n = self.window.default_route
                self.window.rows[n].cb.set_active(False)
            self.window.default_route = self.interface.id
            run_cmd(['ip', 'route', 'add', 'default', 'scope', 'global',
                     'nexthop', 'via', self.curr_network.gateway, 'dev',
                     self.interface.device])
        else:
            if self.window.default_route != self.interface.id:
                print('ERROR')
            self.window.default_route = None
            run_cmd(['ip', 'route', 'del', 'default'])

    def on_switch_activated(self, switch, gparam, iface):
        net = self.curr_network
        if net is None:
            print('ERROR: current network unset')
            return
        table = str(iface.id + 1)
        if switch.get_active():
            run_cmd(['ip', 'link', 'set', iface.device, 'up'])
            run_cmd(['ip', 'addr', 'flush', 'dev', iface.device])
            if iface.type == 'WiFi':
                run_cmd(['iwconfig', iface.device, 'essid', net.ssid])
            run_cmd(['ip', 'addr', 'add', '{}/{}'.format(net.ip, net.mask),
                     'dev', iface.device])
            run_cmd(['ip', 'rule', 'add', 'from', net.ip, 'table', table])
            run_cmd(['ip', 'route', 'add', net.network, 'dev', iface.device,
                     'scope', 'link', 'table', table])
            run_cmd(['ip', 'route', 'add', 'default', 'via', net.gateway, 'dev',
                     iface.device, 'table', table])
            if self.window.default_route is None:
                self.cb.set_active(True)
            iface.is_up = True
            self.cb.set_sensitive(True)
            self.cbt.set_sensitive(False)
        else:
            # remove routes
            run_cmd(['ip', 'route', 'del', net.network, 'table', table])
            run_cmd(['ip', 'route', 'del', 'default', 'table', table])
            run_cmd(['ip', 'rule', 'del', 'from', net.ip, 'table', table])
            # change default route to an active interface
            if self.window.default_route == iface.id:
                self.cb.set_active(False)
                for i, iface2 in enumerate(self.window.interfaces):
                    if iface2 == iface:
                        continue
                    if iface2.is_up:
                        # set i as default route
                        self.window.rows[i].cb.set_active(True)
                        break
            # bring interface down
            run_cmd(['ip', 'addr', 'del', '{}/{}'.format(net.ip, net.mask),
                     'dev', iface.device])
            run_cmd(['ip', 'link', 'set', iface.device, 'down'])
            iface.is_up = False
            self.cb.set_sensitive(False)
            self.cbt.set_sensitive(True)


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="COMBO Client")
        self.set_resizable(False)

        self.read_config()

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.add(self.list_box)

        self.default_route = None

        network_dct = {}
        for net in self.networks:
            if net.type not in network_dct:
                network_dct[net.type] = [net]
            else:
                network_dct[net.type].append(net)
        network_idx = {}
        for k in network_dct.keys():
            network_idx[k] = 0

        self.rows = []
        for iface in self.interfaces:
            try:
                n_lst = network_dct[iface.type]
                sel_idx = network_idx[iface.type]
                network_idx[iface.type] = (sel_idx + 1) % len(n_lst)
            except KeyError:
                n_lst = []
                sel_idx = None
            row = MyListBoxRow(iface, n_lst, sel_idx, self)
            self.rows.append(row)
            self.list_box.insert(row, -1)

    def read_config(self):
        self.interfaces = []
        self.networks = []
        with open('config.json') as f:
            conf = json.load(f)
            for i, dct in enumerate(conf['interfaces']):
                self.interfaces.append(Interface(i, **dct))
            for dct in conf['networks']:
                self.networks.append(Network(**dct))


def run_cmd(cmd):
    print(' '.join(cmd))
    if not test:
        ret = subprocess.call(cmd)
    else:
        ret = 0
    return ret


test = False
run_cmd(['rfkill', 'unblock', 'wifi'])
win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
