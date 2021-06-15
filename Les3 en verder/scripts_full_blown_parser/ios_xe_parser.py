from .utils import ReSearcher, Tree, get_value, get_key, splitrange
from .utils import prev_cur_generator, InterfaceParser


def ios_xe_parser(configfile):

    """
    This function parses banners, interface, vlan, global and hierarchical
    config items into a Python data structure
    """

    with open(configfile, 'r') as lines:
        
        match = ReSearcher()
        tree = Tree()

        key_exceptions = ['ip vrf forwarding']
        key_length = {1: ['hold-queue', 'standby', 'channel-group',
                          'description'],
                      2: ['switchport port-security', 'ip', 'spanning-tree',
                          'speed auto', 'srr-queue bandwidth']}
                      
        list_items = ['switchport trunk allowed vlan', 'standby', 'ip address',
                      'ip helper-address', 'logging event']
        
        intf_parser = InterfaceParser(list_items, key_exceptions, key_length)

        context = ''
        global_cfg = []
        hierarc_cfg = [] # Individual hierarchical config part
        hierarc_cfgs = [] # list with all individual hierarchical config parts
              
        for previous_line, line in prev_cur_generator(lines):
            
            line = line.rstrip()
            if previous_line is not None:
                previous_line = previous_line.rstrip()

            if match(r'^hostname (.*)', line):
                hostname = format(match.group(1))
                tree['hostname'] = hostname

            if match(r'^interface (.*)', line):
                context = 'port'
                portindex = format(match.group(1))
                tree['port'][portindex] = {}
                intf_parser.initialize_lists()
 
            elif match(r'^vlan ([\d,-]+)', line):
                context = 'vlan'
                for vlan in splitrange(format(match.group(1))):
                    tree['vlan'][vlan] = {}

            elif match(r'^banner (\w+) (\S)', line):
                banner_type = format(match.group(1))
                delimeter_char = format(match.group(2))
                tree['banner'][banner_type]['delimeter_char'] = delimeter_char
                tree['banner'][banner_type]['lines'] = []
                context = 'banner'
                                
            elif context == 'port':

                if match(r'^ no (.*)', line):
                    key = format(match.group(1))
                    value = format(match.group(0))
                    tree['port'][portindex][key] = value

                # interface items are stored with helper class
                elif match('^ .*', line):
                    tree = intf_parser.parse_line(tree, portindex, line)

                elif line.lstrip() == line:
                    context = 'unknown'
                    
            elif context == 'vlan':

                if match(r'^ name (.*)', line):
                    tree['vlan'][vlan]['name'] = format(match.group(1))

                elif match(r'!$', line):
                    context = ''

                elif not line.startswith(' '):
                    global_cfg.append(line)
                    context = ''

            # Both line and previous line are global items                       
            elif line.lstrip() == line and context == '':
                if previous_line is None:
                    pass
                elif not previous_line.startswith('!'):
                    global_cfg.append(previous_line)
    
            # Previous line was beginning of hierarchical item
            elif line.lstrip() != line and context == '':
                hierarc_cfg = []
                hierarc_cfg.append(previous_line)
                context = 'hierarc'

            # Both current and previous line belongs to hierarchical item
            elif line.lstrip() != line and context == 'hierarc':
                hierarc_cfg.append(previous_line)

            # Previous line was last hierarchical item
            elif line == '!' or line.startswith('') and context == 'hierarc':
                hierarc_cfg.append(previous_line)
                hierarc_cfgs.append(hierarc_cfg)
                context = ''

            # Previous line was last hierarchical item and directly followed
            # by start of another item (either global or hieratchical)
            elif line.lstrip() == line and context == 'hierarc':
                hierarc_cfg.append(previous_line)
                hierarc_cfgs.append(hierarc_cfg)
                hierarc_cfg = []
                context = 'unknown'

            elif line.lstrip() == line and context == 'unknown':                
                global_cfg.append(previous_line)
                context = ''

            elif line.lstrip() != line and context == 'unknown':
                hierarc_cfg.append(previous_line)
                context = 'hierarc'
                          
            elif context == 'banner' and not line.startswith(delimeter_char):
                tree['banner'][banner_type]['lines'].append(line)

            elif context == 'banner' and line.startswith(delimeter_char):
                context = ''

        tree['global_cfg'] = global_cfg
        tree['hierarc_cfgs'] = hierarc_cfgs
        tree['os_type'] = 'ios_xe'
        return tree
