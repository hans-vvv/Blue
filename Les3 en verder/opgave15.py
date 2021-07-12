import json

def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)


    # First calculate which Vlans are used in the ports of the access switches
    # From question 7 we know that Vlans 4 and 2005 must be added to Switch1
    # because of the subtended switch.

    # Switch1
    tree = get_tree_by_hostname(trees, 'Switch1')
    result = set()

    for port, portitems in tree['port'].items():
        if portitems.get('switchport access vlan') is not None:
            result.add(portitems['switchport access vlan'])
        if portitems.get('switchport voice vlan') is not None:
            result.add(portitems['switchport voice vlan'])
    result.update(['4', '2005'])

    vlan_allowed_list = ['2', '3', '5', '2018', '2019']

    fmt1 = 'Vlans missing on vlan allowed list on trunk are {}'
    fmt2 = 'Incorrectly vlans on vlan allowed list of trunk are {}'
    print(fmt1.format(result - set(vlan_allowed_list)))
    print(fmt2.format(set(vlan_allowed_list) - result))


    # # Switch2
    tree = get_tree_by_hostname(trees, 'Switch2')
    result = set()

    for port, portitems in tree['port'].items():
        if portitems.get('switchport access vlan') is not None:
            result.add(portitems['switchport access vlan'])
        if portitems.get('switchport voice vlan') is not None:
            result.add(portitems['switchport voice vlan'])
    
    vlan_allowed_list = ['2', '3', '5', '2018', '2019']

    fmt1 = 'Vlans missing on vlan allowed list on trunk are {}'
    fmt2 = 'Incorrectly vlans on vlan allowed list of trunk are {}'
    print(fmt1.format(result - set(vlan_allowed_list)))
    print(fmt2.format(set(vlan_allowed_list) - result))
    
    
if __name__ == "__main__":
    main()
