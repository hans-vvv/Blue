from ansible.module_utils.basic import *


def find_mgmt_port(mgmt_ip, route_table):

    """
    This function finds management port based on corresponding management
    IP address and parsed routing table (NTC templates)
    """

    result = {'ansible_facts':{}}

    try:
        for entry in route_table:
            if entry['network'] == mgmt_ip and entry['mask'] == '32':
                result['ansible_facts']['mgmt_port'] = entry['nexthop_if']
                break

        return (0, (result))
    except RuntimeError:
        return (1, ('A runtime error occured'))


def main():
    """
    Main function for Ansible module
    """
    argument_spec = {
        'mgmt_ip': {'type': 'str'},
        'route_table': {'type': 'list'}
    }
    module = AnsibleModule(argument_spec=argument_spec)

    code, response = find_mgmt_port(module.params["mgmt_ip"], module.params["route_table"])
    if code == 1:
        module.fail_json(msg=response)
    else:
        module.exit_json(**response)

    return code


main()
