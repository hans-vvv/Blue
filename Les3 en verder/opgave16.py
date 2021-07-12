import json

def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)

    # Definition of an unused VRF is if a globally defined VRF is not used on
    # any interface.

    # Globally defined VRF's
    tree = get_tree_by_hostname(trees, 'Router1')
    globally_vrfs = []
    for hierarc_cfg in tree['hierarc_cfgs']:
        if hierarc_cfg[0].startswith('ip vrf'):
            globally_vrfs.append(hierarc_cfg[0][-1])
    #print(globally_vrfs)

    # VRF's present on interfaces:
    interface_vrfs = set()
    for portitems in tree['port'].values():
        if portitems.get('ip vrf forwarding') is not None:
           interface_vrfs.add(portitems['ip vrf forwarding'])

    print('The unused VRFs are {}'.format(set(globally_vrfs) - interface_vrfs))
            
            
    
if __name__ == "__main__":
    main()
