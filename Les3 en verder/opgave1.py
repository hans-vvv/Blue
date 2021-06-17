import json
from collections import defaultdict


def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)

    devicenames = []
    for tree in trees:
        devicenames.append(tree['hostname'])
    # print(devicenames)

    access_ports = defaultdict(list) # list with ports per device
    for devicename in devicenames:
        tree = get_tree_by_hostname(trees, devicename)
        for port, portitems in tree['port'].items():
            if (portitems.get('switchport mode') == 'access' and
                    portitems.get('switchport voice vlan') is None):
                access_ports[devicename].append(port)
    # print(access_ports)

    for devicename in access_ports:
        for port in access_ports[devicename]:
            print(devicename, port)
   

if __name__ == "__main__":
    main()
