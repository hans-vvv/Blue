import os
import json
from glob import glob
from scripts_full_blown_parser.ios_xe_parser import ios_xe_parser


def main():

    current_dir = os.getcwd()
    config_dir = current_dir + '\configs_full_blown_parser'

    os.chdir(config_dir)
    configfiles = [configfile for configfile in glob('*-cfg.txt')]
 
    trees = []
    for configfile in configfiles:
        trees.append(ios_xe_parser(configfile))
    
    os.chdir(current_dir)
    with open('4 - trees.json', 'w') as js:
        json.dump(trees, js, indent=4)

if __name__ == "__main__":
    main()
