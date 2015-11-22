#!/usr/bin/python3
from gi.repository import Gtk, GLib, GObject
import json
import subprocess
import datetime as dt
import threading
from time import sleep
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import urlencode


class NetDevice:
    def __init__(self, name):
        self.name = name
        self.prev_rx_bytes = self._get_rx_bytes()
        self.prev_tx_bytes = self._get_tx_bytes()
        self.ts = dt.datetime.now()
        self.N = 5
        self.buff_rx = [0] * self.N
        self.buff_tx = [0] * self.N
        self.idx = 0

    def get_speed(self):
        rx_bytes = self._get_rx_bytes()
        tx_bytes = self._get_tx_bytes()
        now = dt.datetime.now()
        delta = now - self.ts
        rx_speed = (rx_bytes - self.prev_rx_bytes) / delta.total_seconds()
        tx_speed = (tx_bytes - self.prev_tx_bytes) / delta.total_seconds()
        self.ts = now
        self.buff_rx[self.idx] = rx_speed
        self.buff_tx[self.idx] = tx_speed
        self.idx = (self.idx + 1) % self.N
        self.prev_rx_bytes = rx_bytes
        self.prev_tx_bytes = tx_bytes
        avg_rx = sum(self.buff_rx) / self.N
        avg_tx = sum(self.buff_tx) / self.N
        return (avg_rx, avg_tx)

    def _get_rx_bytes(self):
        fn = '/sys/class/net/{}/statistics/rx_bytes'.format(self.name)
        with open(fn) as f:
            rx_bytes = int(f.read())
        return rx_bytes

    def _get_tx_bytes(self):
        fn = '/sys/class/net/{}/statistics/tx_bytes'.format(self.name)
        with open(fn) as f:
            tx_bytes = int(f.read())
        return tx_bytes


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


def select_network_1(name):
    for row in win.rows:
        if row.curr_network.name == name and row.interface.is_up:
            return
    for net in win.networks:
        if net.name == name:
            break
    print(net)
    n = 0
    for net2 in win.networks:
        if net2.type != net.type:
            continue
        if net2 == net:
            break
        n += 1
    print(n)
    for i, iface in enumerate(win.interfaces):
        if iface.type == net.type:
            break
    print(i, iface)
    row = win.rows[i]
    if row.sw.get_active():
        row.sw.set_active(False)
    row.cbt.set_active(n)
    row.sw.set_active(True)


def select_network_2(name):
    for row in win.rows:
        if row.curr_network.name == name and row.interface.is_up:
            return
    for net in win.networks:
        if net.name == name:
            break
    print(net)
    n = 0
    for net2 in win.networks:
        if net2.type != net.type:
            continue
        if net2 == net:
            break
        n += 1
    print(n)
    old_found = False
    for i_old, iface_old in enumerate(win.interfaces):
        if iface_old.type == net.type and iface_old.is_up:
            old_found = True
            break
    if old_found:
        print('old', i_old, iface_old)
    for i_new, iface_new in enumerate(win.interfaces):
        if iface_new.type == net.type and not iface_new.is_up:
            break
    print('new', i_new, iface_new)
    row_new = win.rows[i_new]
    row_new.cbt.set_active(n)
    row_new.sw.set_active(True)
    if old_found:
        row_old = win.rows[i_old]
        row_old.sw.set_active(False)


def update_server():
    while True:
        rx_speed = 0.0
        tx_speed = 0.0
        for net_dev in net_dev_lst:
            rxs, txs = net_dev.get_speed()
            rx_speed += rxs
            tx_speed += txs
        rx_speed /= 1024.0
        tx_speed /= 1024.0
        qs = urlencode({'c': CLIENT_NAME, 'ul': tx_speed, 'dl': rx_speed})
        url = 'http://{}:{}/main/setspeed/?{}'.format(SERVER, PORT, qs)
        print('Update speed: UL={:.1f} KiBps DL={:.1f} KiBps'.format(tx_speed,
                                                                     rx_speed))
        try:
            resp = urlopen(url, timeout=5)
        except URLError:
            print('Could not connect to server.')
        else:
            print('OK')

        url = 'http://{}:{}/main/getnetwork/?c={}'.format(SERVER, PORT, CLIENT_NAME)
        try:
            resp = urlopen(url, timeout=5)
        except URLError:
            print('Could not connect to server.')
        else:
            conn = json.loads(resp.read().decode('utf-8'))
            print('Network name: {}'.format(conn))
            # GLib.idle_add(select_network_1, conn)
            GLib.idle_add(select_network_2, conn)
        sleep(3)


# SERVER = '192.168.1.4'
SERVER = '127.0.0.1'
PORT = 8000
CLIENT_NAME = 'client_1'

test = True
run_cmd(['rfkill', 'unblock', 'wifi'])

GObject.threads_init()

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

net_dev_lst = []
for iface in win.interfaces:
    net_dev_lst.append(NetDevice(iface.device))

thread = threading.Thread(target=update_server)
thread.daemon = True
thread.start()

Gtk.main()
