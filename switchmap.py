import yaml
from re import findall
from netmiko import ConnectHandler
from netmiko import exceptions

def send_command(device_name, device_info):
    net_connect = ConnectHandler(**device_info)
    print(f'[*] {device_name}: Retrieving device mac-address table')
    return net_connect.send_command('show mac-address')

def get_device_port_map(switch_output):
    switch_port_mac = findall(".{6}-.{6} [0-9]+", switch_output)
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
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    main()
    print('--------------------')
except (TypeError, yaml.scanner.ScannerError):
    print(f'[-] Incorrect configuration file')