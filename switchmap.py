'''
Author: q0r3y
Date: 2022-11-30
Notes:
This script is still being developed. Currently, it grabs all the MAC
addresses on an HP Procurve switch and filters out which ones have a
single device connected to them. In the future it will except a file 
exported by DHCP in order to generate a CSV file which will provide a 
quick and easy view of the devices connected to a network, their MAC 
address, IP address, hostname and which switch port they are plugged 
in to. 
'''

import yaml
from re import findall
from netmiko import exceptions
from netmiko import ConnectHandler

def send_command(device_name, device_info):
    net_connect = ConnectHandler(**device_info)
    print(f'[*] {device_name}: Retrieving device mac-address table')
    return net_connect.send_command('show mac-address')

'''
Because "show mac-address" returns all the learned MAC addresses on
the switch, including trunk ports, we need to filter out any port 
that has more than one MAC address on it.
'''
def get_device_port_map(switch_output):
    hp_show_mac_address_regex = ".{6}-.{6} [0-9]+"
    switch_port_mac = findall(hp_show_mac_address_regex, switch_output)
    split_port_mac = list(map(lambda i: i.split(), switch_port_mac))
    ports = [port for mac,port in split_port_mac]
    unique_ports = [i for i in ports if ports.count(i) == 1]
    device_port_dict = {port:mac for mac,port in split_port_mac if port in unique_ports}
    return device_port_dict

def main():
    for device_name in config:
        try:
            device_info = config[device_name]
            print(f'[*] {device_name}: Initiating connection..')
            switch_output = send_command(device_name, device_info)
            device_port_map = get_device_port_map(switch_output)
            print(device_port_map)
        except exceptions.NetmikoAuthenticationException:
            print(f'[-] {device_name}: Invalid Credentials.')
        except exceptions.NetmikoTimeoutException:
            print(f'[-] {device_name}: Incorrect hostname or IP address.')

try:
    print('--- SwitchMap.py ---')
    with open("config-private.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    main()
    print('--------------------')
except (TypeError, yaml.scanner.ScannerError):
    print(f'[-] Incorrect configuration file')