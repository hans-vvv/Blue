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

    tree = get_tree_by_hostname(trees, 'Switch1')
    result = set()

    for port, portitems in tree['port'].items():
        if portitems.get('switchport access vlan') is not None:
            result.add(portitems['switchport access vlan'])
        if portitems.get('switchport voice vlan') is not None:
            result.add(portitems['switchport voice vlan'])

    desktop_vlans = {'4', '2005'}

    result.update(desktop_vlans)
            

    print(sorted(list(result), key=int))
        
   



    

   

if __name__ == "__main__":
    main()
