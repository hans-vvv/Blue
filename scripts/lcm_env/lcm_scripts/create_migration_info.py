from copy import deepcopy
from collections import defaultdict, namedtuple
from pol_utils import *
import ipaddress
import uuid
import json


def create_migration_info(excel_data, stackconfigs, old_config_data):
    """
    This function creates a Tree object containing all site specific data for
    all new network devices. So in general the following data is present in the
    object: Vlan info, IP info and switchport info. The switchport information
    is "migrated" using a 'old hostname/old port' to a 'new hostname/new port'
    mapping. This mapping is to be present in the Excel file. The object is also
    printed in a JSON formatted file.

    :param excel_data: dictionary containing data from Excel file.
    :param stackconfigs: dictionary with data of all stacks.
    :param old_config_data: data from old devices.
    :return: Configuration object with site specific data of new devices.
    """
    match = ReSearcher()

    site_migration = excel_data['site_migration']

           
    host_port_map = {}  # Uni migration
    for row in excel_data['uni_migration']:
        host_port_map[(row.old_hostname, row.old_port)] = \
            (row.new_hostname, row.new_port)

    
    # Configuration object for all new devices
    new_config_data = Tree()

    old_hostnames = [tree['hostname'] for tree in old_config_data]
    for old_hostname in old_hostnames:
        tree = get_tree_by_hostname(old_config_data, old_hostname)

        for port, portitems in tree['port'].items():
            portkeys = portitems.keys()

            if (old_hostname, port) not in host_port_map.keys():
                continue

            if (portitems.get('switchport mode') == 'access'
                    and 'switchport access vlan' in portkeys):
                    
                data_vlan = portitems['switchport access vlan']
                voice_vlan = portitems.get('switchport voice vlan')
                new_hostname = host_port_map[(old_hostname, port)][0]
                new_port = host_port_map[(old_hostname, port)][1]
                new_config_data[new_hostname]['port'][new_port][
                    'switchport access vlan'] = data_vlan
                new_config_data[new_hostname]['port'][new_port][
                    'switchport voice vlan'] = voice_vlan


    new_devices = [hostname for hostname in stackconfigs]
    old_routers = [row.old_devicename for row in site_migration
                   if row.old_devicerole == 'router']
    new_routers = [hostname for hostname in stackconfigs
                   if stackconfigs[hostname].devicerole == 'router']
    new_switches = [hostname for hostname in stackconfigs
                    if stackconfigs[hostname].devicerole == 'switch']
    old_mgmt_vlan = [row.from_vlan for row in site_migration
                     if row.vlan_type == 'mgmt'][0]
    new_mgmt_vlan = [row.to_vlan for row in site_migration
                     if row.vlan_type == 'mgmt'][0]

    device_mgmt_prefix_map = {}
    for row in site_migration:
        if row.new_devicename is None:
            continue
        device_mgmt_prefix_map[row.new_devicename] = row.new_mgmt_prefix

    # Create Vlan to new VRF mapping
    vlan_vrf_map = {}
    for row in site_migration:
        vlan_vrf_map[row.from_vlan] = row.vrf

    # Mgmt IP interface
    for device in device_mgmt_prefix_map:
        ip_prefix = device_mgmt_prefix_map[device]
        host = str(ipaddress.IPv4Interface(ip_prefix).ip)
        mask = str(ipaddress.IPv4Interface(ip_prefix).netmask)
        mgmt_interface = 'Vlan' + new_mgmt_vlan
        new_config_data[device]['port'][mgmt_interface]['ip address'] = \
            host + ' ' + mask
        new_config_data[device]['port'][mgmt_interface]['ip vrf forwarding'] = \
            'global'
    # EGL-B to EGL-B migration
    if len(old_routers) == 1 and len(new_routers) == 1:
        tree = get_tree_by_hostname(old_config_data, old_routers[0])
        for port, portitems in tree['port'].items():
            if 'Vlan' not in port:
                continue
            if 'Vlan' + old_mgmt_vlan == port:
                continue
            ip_address = portitems['ip address']
            vlan = port.split('Vlan')[1]
            vrf = vlan_vrf_map[vlan]
            new_config_data[
                new_routers[0]]['port'][port]['ip address'] = ip_address
            new_config_data[
                new_routers[0]]['port'][port]['ip vrf forwarding'] = vrf

    # EGL-C to EGL-B migration
    elif len(old_routers) == 2 and len(new_routers) == 1:
        tree = get_tree_by_hostname(old_config_data, old_routers[0])
        for port, portitems in tree['port'].items():
            if 'Vlan' not in port:
                continue
            if 'Vlan' + old_mgmt_vlan == port:
                continue

            vlan = port.split('Vlan')[1]
            vrf = vlan_vrf_map[vlan]
            new_config_data[
                new_routers[0]]['port'][port]['ip vrf forwarding'] = vrf

            hsrp_address = None
            if 'standby' in portitems.keys():
                ip_mask = portitems['ip address'].split()[1]
                for item in portitems['standby']:
                    if match(r'^\d+ ip (\d+\.\d+\.\d+\.\d+)', item):
                        hsrp_address = match.group(1)
                new_config_data[new_routers[0]]['port'][port]['ip address'] = \
                    hsrp_address + ' ' + ip_mask
            else:
                ip_address = portitems['ip address']
                new_config_data[new_routers[0]]['port'][port]['ip address'] = \
                    ip_address

    # EGL-C to EGL-C migration
    elif len(old_routers) == 2 and len(new_routers) == 2:
        index = 0
        for old_router, new_router in zip(old_routers, new_routers):
            tree = get_tree_by_hostname(old_config_data, old_router)
            for port, portitems in tree['port'].items():
                if 'Vlan' not in port:
                    continue
                if 'Vlan' + old_mgmt_vlan == port:
                    continue

                vlan = port.split('Vlan')[1]
                vrf = vlan_vrf_map[vlan]
                new_config_data[
                    new_router]['port'][port]['ip vrf forwarding'] = vrf

                hsrp_address = None
                if 'standby' in portitems.keys():
                    standby = []
                    for item in portitems['standby']:
                        if match(r'^\d+ ip (\d+\.\d+\.\d+\.\d+)', item):
                            hsrp_address = match.group(1)
                    new_config_data[new_router]['port'][port]['standby'] = \
                        standby
                    standby.append('1 ip ' + hsrp_address)
                    standby.append('1 priority 254') if index == 0 else standby.append(
                        '1 priority 100')

                ip_address = portitems['ip address']
                new_config_data[new_router]['port'][port]['ip address'] = \
                    ip_address
            index += 1

        # Configure ether channel between both routers
        peer_router = {new_routers[0]: new_routers[1],
                       new_routers[1]: new_routers[0]}
        for router in peer_router:
            for port, items in stackconfigs[router].nni_port_assignment.items():
                remote_device = items[0]
                if remote_device != peer_router[router]:
                    continue

                new_config_data[router]['port'][port]['channel-group'] = \
                    '1 mode active'
                new_config_data[router]['port'][port]['description'] = \
                    remote_device + ' ' + short_port_index(port)
            new_config_data[
                router]['port']['Port-channel1']['switchport trunk encapsulation'] = 'dot1q'
            new_config_data[
                router]['port']['Port-channel1']['switchport mode'] = 'trunk'
            new_config_data[router]['port']['Port-channel1'][
                'description'] = peer_router[router]


    # Create VLAN allowed list for devices with switch role.
    vlan_allow_set = defaultdict(set)
    for switch in new_switches:
        for port, portitems in new_config_data[switch]['port'].items():
            data_vlan = portitems.get('switchport access vlan')
            voice_vlan = portitems.get('switchport voice vlan')
            if data_vlan is not None:
                vlan_allow_set[switch].add(data_vlan)
            if voice_vlan is not None:
                vlan_allow_set[switch].add(voice_vlan)  
        vlan_allow_set[switch].add(new_mgmt_vlan)

    vlan_allow_list = defaultdict(list)
    for switch in vlan_allow_set:
        vlan_allow_list[switch] = sorted(list(vlan_allow_set[switch]), key=int)

    for switch in new_switches:
        for port, items in stackconfigs[switch].nni_port_assignment.items():
            if items == ('', ''):
                continue

            remote_device = items[0]
            remote_port = items[1]

            
            new_config_data[switch]['port'][port]['switchport trunk encapsulation'] = 'dot1q'
            new_config_data[switch]['port'][port]['switchport mode'] = 'trunk'
            new_config_data[switch]['port'][port]['vlan_allow_list'] = \
                vlan_allow_list[switch]
            new_config_data[switch]['port'][port]['description'] = \
                remote_device + ' ' + short_port_index(remote_port)

            # update remote router ports. Avoid multiple references
            # to vlan_allow_list using deepcopy. Else new_config
            # object cannot be updated later on.
            vlan_allow_router = deepcopy(vlan_allow_list[switch])
            new_config_data[remote_device]['port'][remote_port][
                'switchport mode'] = 'trunk'
            new_config_data[remote_device]['port'][remote_port][
                'switchport trunk encapsulation'] = 'dot1q'
            new_config_data[remote_device]['port'][remote_port][
                'vlan_allow_list'] = vlan_allow_router
            description = switch + ' ' + short_port_index(port)
            new_config_data[
                remote_device]['port'][remote_port]['description'] = description


    # Process VLAN information
    # Collect subnet information from SVI's
    # Later check both routers and compare
    vlan_ipv4network_map = {}
    tree = get_tree_by_hostname(old_config_data, old_routers[0])
    for port, portitems in tree['port'].items():
        if 'Vlan' not in port:
            continue
        if 'Vlan' + old_mgmt_vlan == port:
            continue
        ip_address = portitems['ip address']
        host, mask = ip_address.split()[0], ip_address.split()[1]
        network = ipaddress.IPv4Interface(host + '/' + mask).network
        vlan_id = port.split('Vlan')[1]
        vlan_ipv4network_map[vlan_id] = str(network)

    # Mgmt VLAN
    for row in site_migration:
        network = ipaddress.IPv4Interface(row.new_mgmt_prefix).network
        vlan_ipv4network_map[new_mgmt_vlan] = str(network)
        break

    # Construct VLAN names
    vlan_names = {}
    for row in site_migration:
        if row.vlan_type == 'data':
            vlan_name = 'VRF_{}_USER_{}'.format(
                row.vrf, vlan_ipv4network_map[row.from_vlan])
            vlan_names[row.from_vlan] = vlan_name
        elif row.vlan_type == 'voice':
            vlan_name = 'VRF_{}_VOIP_{}'.format(
                row.vrf, vlan_ipv4network_map[row.from_vlan])
            vlan_names[row.from_vlan] = vlan_name
        elif row.vlan_type == 'transit':
            vlan_name = 'VRF_{}_Transit_{}'.format(
                row.vrf, vlan_ipv4network_map[row.from_vlan])
            vlan_names[row.from_vlan] = vlan_name
        elif row.vlan_type is None and row.from_vlan is not None:
            vlan_name = 'VRF_{}_{}_{}'.format(
                row.vrf, row.base_vlan_name,
                vlan_ipv4network_map[row.from_vlan])
            vlan_names[row.from_vlan] = vlan_name
        elif row.vlan_type == 'mgmt':
            vlan_name = 'OOB_{}'.format(vlan_ipv4network_map[new_mgmt_vlan])
            vlan_names[new_mgmt_vlan] = vlan_name

    # Add Vlan's to VLAN database of devices
    for switch in vlan_allow_list:
        for vlan in vlan_allow_list[switch]:
            new_config_data[switch]['vlan'][vlan]['name'] = vlan_names[vlan]
    for new_router in new_routers:
        for vlan in vlan_names:
            new_config_data[new_router]['vlan'][vlan]['name'] = vlan_names[vlan]

    # Static routes, check on first router, later check on both
    # Collect route_info
    old_static_route_info = defaultdict(list)
    new_static_route_info = defaultdict(list)
    tree = get_tree_by_hostname(old_config_data, old_routers[0])
    for vrf in tree['static']['vrf']:
        for ip_route_info in tree['static']['vrf'][vrf].values():
            old_static_route_info[vrf].append(ip_route_info)
    for port, portitems in tree['port'].items():
        if 'Vlan' not in port:
            continue
        if 'Vlan' + old_mgmt_vlan == port:
            continue
        ip_address = portitems['ip address']
        new_vrf = new_config_data[
            new_routers[0]]['port'][port].get('ip vrf forwarding')
        new_vrf = new_vrf if new_vrf is not None else 'global'
        host, mask = ip_address.split()[0], ip_address.split()[1]
        network = ipaddress.IPv4Interface(host + '/' + mask).network

        # If next-hop of static route is in IPv4 network of a SVI interface
        # then static route will be migrated
        for vrf, ip_route_info in old_static_route_info.items():
            if vrf == 'global' and new_mgmt_vlan != old_mgmt_vlan:
                continue
            for route in ip_route_info:
                next_hop = route.split()[2]
                if ipaddress.ip_address(next_hop) in \
                        ipaddress.ip_network(str(network)):
                    new_static_route_info[new_vrf] = ip_route_info

    for router in new_routers:
        for new_vrf, statics in new_static_route_info.items():
            for static_route in statics:
                key = uuid.uuid4().hex
                new_config_data[router]['static'][new_vrf][key] = static_route

    # Mgmt route.
    new_mgmt_gw = [row.new_mgmt_gw for row in site_migration][0]
    for hostname in new_devices:
        key = uuid.uuid4().hex
        new_config_data[hostname]['static']['global'][key] = \
            '0.0.0.0 0.0.0.0 ' + new_mgmt_gw

    with open('new_configs.json', 'w') as f:
        json.dump(new_config_data, f, indent=4)

    return new_config_data
