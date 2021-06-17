import json
from collections import defaultdict


def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    with open('trees.json', 'r') as file:
        trees = json.load(file)

    devicenames = []
    for tree in trees:
        devicenames.append(tree['hostname'])
    # print(devicenames)

    empty_ports = defaultdict(list) # list with empty ports per device
    # The problem here is to define the definition of empty:
    # 1. If it is in shutdown and no switchport state
    # 2. If it has no configuration at all
    for devicename in devicenames:
        tree = get_tree_by_hostname(trees, devicename)
        for port, portitems in tree['port'].items():
            if (not portitems or
                    (portitems.get('shutdown') == 'shutdown' and
                     portitems.get('switchport') == 'no switchport')):
                empty_ports[devicename].append(port)
    print(empty_ports)

    for devicename in empty_ports:
        for port in empty_ports[devicename]:
            print(devicename, port)
  

if __name__ == "__main__":
    main()
