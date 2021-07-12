import json


def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree

def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)

    tree = get_tree_by_hostname(trees, 'Router1')
    port_hsrp_prio_router1 = {}
    for port, portitems in tree['port'].items():
        if 'Vlan' not in port:
            continue
        if portitems.get('standby') is None:
            continue
        for line in portitems['standby']:
            if 'priority' not in line:
                continue
            port_hsrp_prio_router1[port] = line.split()[-1]

    tree = get_tree_by_hostname(trees, 'Router2')
    port_hsrp_prio_router2 = {}
    for port, portitems in tree['port'].items():
        if 'Vlan' not in port:
            continue
        if portitems.get('standby') is None:
            continue
        for line in portitems['standby']:
            if 'priority' not in line:
                continue
            port_hsrp_prio_router2[port] = line.split()[-1]
            

    for port1 in port_hsrp_prio_router1: # shortcut, I Don't use keys() method here
        for port2 in port_hsrp_prio_router2:
            if port1 == port2:
                if int(port_hsrp_prio_router1[port1]) <= int(port_hsrp_prio_router2[port2]):
                    print('Design validation detected on port {}'.format(port1))

if __name__ == "__main__":
    main()




        

