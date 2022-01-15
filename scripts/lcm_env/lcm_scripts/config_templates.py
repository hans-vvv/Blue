from jinja2 import Environment, FileSystemLoader, StrictUndefined


def _j2_parser(j2template_name, **kwargs):
    file_loader = FileSystemLoader('j2templates')
    env = Environment(
        loader=file_loader, trim_blocks=True, lstrip_blocks=True,
        undefined=StrictUndefined
    )
    j2template = env.get_template(j2template_name)
    return j2template.render(**kwargs)


def l2_vlan(vlan_id, vlan_name=None):
    kwargs = {'vlan_id': vlan_id, 'vlan_name': vlan_name}
    return _j2_parser('l2_vlan.txt', **kwargs)


def l3_vlan(interface, vlan_ip_plus_mask, hsrp_address=None, description=None,
            hsrp_state=None, vrf=None, helpers=None):

    kwargs = {'interface': interface, 'vlan_ip_plus_mask': vlan_ip_plus_mask,
              'hsrp_address': hsrp_address, 'description': description,
              'hsrp_state': hsrp_state, 'vrf': vrf, 'helpers': helpers}
    return _j2_parser('l3_vlan.txt', **kwargs)


def switchport(interface, description=None, switchport_trunk_encapsulation=None,
               switchport_mode=None,
               switchport_accces_vlan=None, source_template=None,
               vlan_allow_list_cs=None, channel_group=None,
               switchport_voice_vlan=None):

    kwargs = {'interface': interface, 'description': description,
              'switchport_trunk_encapsulation': switchport_trunk_encapsulation, 
              'switchport_mode': switchport_mode,
              'switchport_access_vlan': switchport_accces_vlan,
              'switchport_voice_vlan': switchport_voice_vlan,
              'source_template': source_template,
              'vlan_allow_list_cs': vlan_allow_list_cs,
              'channel_group': channel_group}
    return _j2_parser('switchport.txt', **kwargs)


def static_route(vrf, route_info):

    kwargs = {'vrf': vrf, 'route_info': route_info}
    return _j2_parser('static-route.txt', **kwargs)


def generics(hostname):
    kwargs = {'hostname': hostname}
    return _j2_parser('generics.txt', **kwargs)


def template(name, data_vlan, voice_vlan):
    kwargs = {'name': name, 'data_vlan': data_vlan,
              'voice_vlan': voice_vlan}
    return _j2_parser('template.txt', **kwargs)


def migrate_l2_vlan(old_vlan, new_vlan, vlan_name, port_list, template_names):
    kwargs = {'old_vlan': old_vlan, 'new_vlan': new_vlan,
              'vlan_name': vlan_name, 'port_list': port_list,
              'template_names': template_names}
    return _j2_parser('migrate_l2_vlan.txt', **kwargs)


def migrate_l3_vlan(old_vlan, new_vlan, ip_address, description, vrf,
                    hsrp_address=None, hsrp_state=None):
    kwargs = {'old_vlan': old_vlan, 'new_vlan': new_vlan,
              'ip_address': ip_address, 'description': description,
              'vrf': vrf, 'hsrp_address': hsrp_address,
              'hsrp_state': hsrp_state}
    return _j2_parser('migrate_l3_vlan.txt', **kwargs)
