#!/usr/bin/python3
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep
import json
import subprocess
import re


SERVER = '192.168.1.4'
PORT = 8000
CLIENT_NAME = 'client_1'


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
    if is_active('wlp3s0'):
        return
    print('Enabling WiFi i/f.')
    cmd = ['nmcli', 'device', 'connect', 'wlp3s0']
    ret = subprocess.call(cmd)
    print('nmcli return code: {}'.format(ret))

def wifi_down():
    if not is_active('wlp3s0'):
        return
    print('Disabling WiFi i/f.')
    cmd = ['nmcli', 'device', 'disconnect', 'wlp3s0']
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


while True:
    url = 'http://{}:{}/main/getnetwork/?c={}'.format(SERVER, PORT, CLIENT_NAME)
    try:
        resp = urlopen(url, timeout=5)
    except URLError:
        print('Could not connect to server.')
    else:
        conn = json.loads(resp.read().decode('utf-8'))
        print('Network name: {}'.format(conn))
        if conn != current_conn and len(conn) > 0:
            netw_type = get_netw_type(conn)
            if netw_type == 'WiFi':
                lte_down()
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
    sleep(3)
