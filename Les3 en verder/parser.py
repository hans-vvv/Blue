import os
import json
from glob import glob
from collections import defaultdict
from scripts_full_blown_parser.ios_xe_parser import ios_xe_parser


def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    current_dir = os.getcwd()
    config_dir = current_dir + '\configs_full_blown_parser'

    os.chdir(config_dir)
    configfiles = [configfile for configfile in glob('*-cfg.txt')]
 
    trees = []
    for configfile in configfiles:
        trees.append(ios_xe_parser(configfile))
    
    os.chdir(current_dir)
    with open('trees.json', 'w') as js:
        json.dump(trees, js, indent=4)

    devicenames = []
    for tree in trees:
        devicenames.append(tree['hostname'])

    access_ports = defaultdict(list)
    for devicename in devicenames:
        tree = get_tree_by_hostname(trees, devicename)
        for port, portitems in tree['port'].items():
            if portitems.get('switchport mode') == 'access':
                access_ports[devicename].append(port)

    # print(access_ports)
    for devicename in access_ports:
        print(devicename)
##        for port in access_ports[device]:
##            print(device, port)
                    
            
            
            
        
        

    

if __name__ == "__main__":
    main()
