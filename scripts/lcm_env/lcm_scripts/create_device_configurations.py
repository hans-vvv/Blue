import os
import shutil
from glob import glob
from pol_utils import *
from lcm_scripts import l2_vlan, l3_vlan, generics, template, switchport
from lcm_scripts import static_route


def create_device_configurations(new_configs):
    """
    Initial device configurations are printed in separate files. These files
    contains enough information so that UNI ports can be migrated from the old
    equipment to the new equipment using these new device configurations.

    :param new_configs: object containing device specific configuration info.
    :return: None
    """

    base_dir = os.getcwd()
    config_dir = base_dir +  '/lcm_configs'
    if os.path.isdir(config_dir):
        shutil.rmtree(config_dir)
    os.mkdir(config_dir)

    fh = {}  # file handle
    for hostname in new_configs:

        fh[hostname] = open(hostname + '-initial.txt', 'w')

        # print generics in configuration file
        config_add = generics(hostname)
        print(config_add, file=fh[hostname])

        # print VLAN databases
        for vlan, name_items in new_configs[hostname]['vlan'].items():
            vlan_name = name_items.get('name')
            config_add = l2_vlan(vlan, vlan_name)
            print(config_add, file=fh[hostname])

        # print configuration templates
        for name, template_items in new_configs[hostname]['template'].items():
            data_vlan = template_items['switchport access vlan']
            voice_vlan = template_items['switchport voice vlan']
            config_add = template(name, data_vlan, voice_vlan)
            print(config_add, file=fh[hostname])

        # print L3 Vlan's
        for port, portitems in new_configs[hostname]['port'].items():
            if 'Vlan' not in port:
                continue
            vlan = port.split('Vlan')[1]
            description = new_configs[hostname]['vlan'][vlan].get('name')
            vlan_ip_plus_mask = portitems['ip address']
            vrf = portitems.get('ip vrf forwarding')

            hsrp_address = portitems.get('standby')[0] \
                if portitems.get('standby') else None
            hsrp_state = portitems.get('standby')[1] \
                if portitems.get('standby') else None

            config_add = l3_vlan(
                port, vlan_ip_plus_mask, description=description, vrf=vrf,
                hsrp_state=hsrp_state, hsrp_address=hsrp_address
            )
            print(config_add, file=fh[hostname])

        # Print switchport interfaces
        for port, portitems in new_configs[hostname]['port'].items():
            if 'Vlan' in port:
                continue
            description = portitems.get('description')
            switchport_trunk_encapsulation = portitems.get('switchport trunk encapsulation')
            switchport_mode = portitems.get('switchport mode')
            switchport_access_vlan = portitems.get('switchport access vlan')
            switchport_voice_vlan = portitems.get('switchport voice vlan')
            source_template = portitems.get('source template')
            vlan_allow_list = portitems.get('vlan_allow_list')
            channel_group = portitems.get('channel-group')
            vlan_allow_list_cs = ','.join(vlan_allow_list) \
                if vlan_allow_list else None

            config_add = switchport(
                port,
                description=description,
                switchport_trunk_encapsulation=switchport_trunk_encapsulation,
                switchport_mode=switchport_mode,
                switchport_accces_vlan=switchport_access_vlan,
                switchport_voice_vlan=switchport_voice_vlan,
                source_template=source_template,
                vlan_allow_list_cs=vlan_allow_list_cs,
                channel_group=channel_group
            )
            print(config_add, file=fh[hostname])

        # Static routes
        for vrf, items in new_configs[hostname]['static'].items():
            for route_info in items.values():
                config_add = static_route(vrf, route_info)
                print(config_add, file=fh[hostname])

        fh[hostname].close()

    move_dir(base_dir, config_dir, pattern='*initial.txt')
