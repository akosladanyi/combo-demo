#!/usr/bin/python3
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import urlencode
from time import sleep
import json
import subprocess
import re
import datetime as dt


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


# SERVER = '192.168.1.4'
SERVER = '127.0.0.1'
PORT = 8000
CLIENT_NAME = 'client_1'
WIFI_1_DEVICE = 'wlp3s0'


def get_netw_type(name):
    if name.startswith('COMBO_WiFi_'):
        return 'WiFi'
    else:
        return 'LTE'


current_conn = None
current_netw_type = 'WiFi'


def is_active(device):
    cmd = ['nmcli', 'device', 'show', device]
    ret = subprocess.check_output(cmd)
    m = re.search('GENERAL\.STATE:\s+(\d+)', ret.decode('utf-8'))
    if m:
        return m.group(1) == '100'
    else:
        return None


def wifi_up():
    if is_active(WIFI_1_DEVICE):
        return
    print('Enabling WiFi i/f.')
    cmd = ['nmcli', 'device', 'connect', WIFI_1_DEVICE]
    ret = subprocess.call(cmd)
    print('nmcli return code: {}'.format(ret))

def wifi_down():
    if not is_active(WIFI_1_DEVICE):
        return
    print('Disabling WiFi i/f.')
    cmd = ['nmcli', 'device', 'disconnect', WIFI_1_DEVICE]
    ret = subprocess.call(cmd)
    print('nmcli return code: {}'.format(ret))

def lte_up():
    if is_active('enp0s26f7u1'):
        return
    print('Enabling LTE i/f.')
    cmd = ['nmcli', 'device', 'connect', 'enp0s26f7u1']
    ret = subprocess.call(cmd)
    print('nmcli return code: {}'.format(ret))

def lte_down():
    if not is_active('enp0s26f7u1'):
        return
    print('Disabling LTE i/f.')
    cmd = ['nmcli', 'device', 'disconnect', 'enp0s26f7u1']
    ret = subprocess.call(cmd)
    print('nmcli return code: {}'.format(ret))


net_dev = NetDevice(WIFI_1_DEVICE)
while True:
    rx_speed, tx_speed = net_dev.get_speed()
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
        if conn != current_conn and len(conn) > 0:
            print('Network name: {} (connecting)'.format(conn))
            netw_type = get_netw_type(conn)
            if netw_type == 'WiFi':
                #lte_down()
                wifi_up()

                print('Connecting to WiFi network.')
                cmd = ['nmcli', 'connection', 'up', 'id', conn]
                print(' '.join(cmd))
                ret = subprocess.call(cmd)
                print('nmcli return code: {}'.format(ret))
                if ret == 0:
                    print('Connected')
                    current_conn = conn
                else:
                    print('Connection failed')
            elif netw_type == 'LTE':
                wifi_down()
                lte_up()
                current_conn = conn
            else:
                print('Unknown network type.')
                continue
        else:
            print('Network name: {} (no change)'.format(conn))
    sleep(3)
