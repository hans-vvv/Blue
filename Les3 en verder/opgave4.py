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

    vlan_db = defaultdict(list)
    for devicename in devicenames:
        tree = get_tree_by_hostname(trees, devicename)
        for vlan, vlanitems in tree['vlan'].items():
            vlan_db[devicename].append(vlan)
    # print(vlan_db)

    for devicename in vlan_db:
        print('The VLANs of device {} are:'.format(devicename))
        for vlan in vlan_db[devicename]:
            print(vlan)
        print()
  

if __name__ == "__main__":
    main()
