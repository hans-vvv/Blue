import os
import argparse
import ipaddress
import configparser
from lcm_scripts import read_excel_data
from pol_utils import move_dir


def transform_data_from_sheets(excel_data):

    data = {}

    # Unpack Excel data
    inventory = excel_data['inventory']
    site_migration = excel_data['site_migration']

    # Create dict for current/old inventory
    inventory_hostnames = [row.hostname for row in inventory if row.hostname is not None]
    inventory_ips = [row.ip_address for row in inventory if row.ip_address is not None]
    inventory_dict = dict(zip(inventory_hostnames, inventory_ips))

    old_devicenames = [row.old_devicename for row in site_migration if row.old_devicename is not None]
    old_deviceips = [inventory_dict[device] for device in old_devicenames]
    
    data['old'] = dict(zip(old_devicenames, old_deviceips))

    # Create dict for staging inventory
    new_mgmt_prefixs = [row.new_mgmt_prefix for row in site_migration if row.new_mgmt_prefix is not None]

    if not new_mgmt_prefixs:
        data['initial_dynamic'] = {}
    else:
        first_prefix = new_mgmt_prefixs[0]
        network = ipaddress.IPv4Interface(first_prefix).network
        host_ips = [str(ip_add) for ip_add in network.hosts()]

        staging_names = []
        for index, _ in enumerate(host_ips):
            staging_names.append('S' + str(index + 1))

        data['initial_dynamic'] = dict(zip(staging_names, host_ips))

    # Create dict for new inventory
    new_devicenames = [row.new_devicename for row in site_migration if row.new_devicename is not None]
    if not new_mgmt_prefixs: # Declared one section above
        data['final'] = {}
    else:
        ips = [str(ipaddress.IPv4Interface(prefix).ip) for prefix in new_mgmt_prefixs]
        data['final'] = dict(zip(new_devicenames, ips))

    return data
 

def gen_ini_file(data, group, filename):
    ''' Takes a dictionary. It creates an INI file'''
    config = configparser.ConfigParser()
    config.add_section(group)
    for key, value in data.items():
        config.set(group,'{} ansible_host'.format(key), value)

    with open(filename, 'w') as f:
        config.write(f, space_around_delimiters=False)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description="LCM inventory generator for Ansible"
    )
    group = arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--old", action="store_true", default=None,
        help="Inventory for old elements"
    )
    group.add_argument(
        "--initial_dynamic", action="store_true", default=None,
        help="Initial dynamic inventory for pushing configs to staged elements"
    )
    group.add_argument(
        "--final", action="store_true", default=None,
        help="Final inventory for pushing final configs to new elements"
    )
    return arg_parser.parse_args()


def main():

    excel_data = read_excel_data('result.xlsx')
    data = transform_data_from_sheets(excel_data)
        
    args = parse_args()

    if args.old:
        gen_ini_file(data['old'], 'old', 'hosts.old')
    elif args.initial_dynamic:
        gen_ini_file(data['initial_dynamic'], 'initial_dynamic', 'hosts.initial_dynamic')
    elif args.final:
        gen_ini_file(data['final'], 'final', 'hosts.final')

    base_dir = os.getcwd()
    working_dir = base_dir + '/ansible_inventory'
    move_dir(base_dir, working_dir, pattern='hosts*')


if __name__ == "__main__":
    main()


