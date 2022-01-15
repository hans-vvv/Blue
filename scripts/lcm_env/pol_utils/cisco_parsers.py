import re
import uuid
from pol_utils import *


def get_value(key, item):
    """
    key + value = interface item
    function returns value for given key and item
    """

    if key.strip() == item.strip():
        return key
    else:
        item = item.lstrip()
        result = re.search('^(' + key + ')(.*)', item)
        value = format(result.group(2)).lstrip()
        return value


def get_key(item, key_length):
    """
    key + value = item
    number of words of key = key_length
    function returns key
    """

    word = item.strip().split()
    if key_length == 0:  # fix
        return item
    elif len(word) == key_length:
        return item
    else:
        return ' '.join(word[0:key_length])


def splitrange(raw_range):
    """
    '1,2,4-6' returns ['1','2','4','5','6']
    'none'    returns ['None']
    """

    m = re.search(r'^(\d+)\-(\d+)$', raw_range)
    if m:
        first = int(format(m.group(1)))
        last = int(format(m.group(2)))
        return [str(i) for i in range(first, last + 1)]

    m = re.search(r'[\d+,-]+', raw_range)
    if m:
        result = []
        for raw_element in format(m.group(0)).split(','):
            if '-' in raw_element:
                for element in splitrange(raw_element):
                    result.append(element)
            else:
                result.append(raw_element)
        return result

    m = re.search(r'^none$', raw_range)
    if m:
        return ['None']



class InterfaceParser:
    """
    Helper class to parse interface items. Items which are
    present in list_items (see __init__) are stored in lists.
    With using the _select_key method the following logic is implemented
    to determine which part of an interface item is considered to be a
    key and which part a value.

    1. First portkey_exceptions list is examined. If an interface item
       contains the words found in this list then key = item in the list
       and value = remaining words of the interface item. If an interface
       item is found then the other methods are not considered.
    2. Key_length dict is examined. If interface item contains an item
       found in a list of the dict then corresponding key (i.e. 1 or 2)
       is used to split the item. The key of the item is equal to the
       number of words of the dict key, the rest of the item = value.
       Example: If line = channel-group 2 mode active, then
       key = "channel-group"  and value = "2 mode active". If an interface
       item is found then the last method is not considered.
    3. Default method. Last word of line = value
       and all preceding words = key.
    """

    def __init__(self, list_items, key_exceptions, key_length):
        self.list_items = list_items
        self.key_exceptions = key_exceptions
        self.key_length = key_length

    def initialize_lists(self):
        self.values = [[] for _ in self.list_items]

    def _get_index(self, line):
        """ Get index by name of lists to store values """
        for index, item in enumerate(self.list_items):
            if line.startswith(item):
                return index

    def _select_key(self, line):
        """ Determine key-value split of items based on algorithm """
        for key in self.key_exceptions:
            if line.startswith(key):
                return key
        for key_length, items in self.key_length.items():
            for item in items:
                if line.startswith(item):
                    return get_key(line, key_length)
        return get_key(line, len(line.split()) - 1)

    def parse_line(self, tree, portindex, line):
        """ Parse line into dict where value is str, list or extended list """
        line = line.lstrip()
        key = self._select_key(line)
        for item in self.list_items:
            if line.startswith(item):
                index = self._get_index(line)
                if line.startswith('switchport trunk allowed vlan'):
                    self.values[index].extend(splitrange(get_value(key, line)))
                    tree['port'][portindex]['vlan_allow_list'] \
                        = self.values[index]
                    return tree
                else:
                    self.values[index].append(get_value(key, line))
                    tree['port'][portindex][item] = self.values[index]
                    return tree
        tree['port'][portindex][key] = get_value(key, line)
        return tree


def ios_xe_parser(configfile):
    """
    This function parses a Cisco IOS configuration file into a nested
    dictionary. It has the following capabilities:
    - All interfaces items are parsed into key-value pairs using a helper class
      (see above) to determine the key and value parts of the interface items.
    - For specific interface items, lists are used to store data.
    - Global config items are stored in a list.
    - All hierarchical items are stored in seperate lists.
    - Banners are stored in a list.
    """

    with open(configfile, 'r') as lines:

        match = ReSearcher()
        tree = Tree()

        key_exceptions = ['ip vrf forwarding']
        key_length = {1: ['hold-queue', 'standby', 'channel-group',
                          'description'],
                      2: ['switchport port-security', 'ip', 'spanning-tree',
                          'speed auto', 'srr-queue bandwidth']
                      }
        list_items = ['switchport trunk allowed vlan', 'standby',
                      'ip helper-address', 'logging event']
        port_parser = InterfaceParser(list_items, key_exceptions, key_length)

        context = ''

        for line in lines:

            if not line.strip():  # skip empty lines
                continue

            line = line.rstrip()

            if match(r'^hostname (.*)', line):
                hostname = format(match.group(1))
                tree['hostname'] = hostname

            elif match(r'^interface (.*)', line):
                context = 'port'
                portindex = format(match.group(1))
                tree['port'][portindex] = {}
                port_parser.initialize_lists()

            elif match(r'^vlan ([\d,-]+)', line):
                context = 'vlan'
                for vlan in splitrange(format(match.group(1))):
                    tree['vlan'][vlan] = {}

            elif match(r'^ip route vrf (\w+) (.*)', line):
                vrf = format(match.group(1))
                route_info = format(match.group(2))
                key = uuid.uuid4().hex
                tree['static']['vrf'][vrf][key] = route_info

            elif match(r'ip route (.*)', line):
                route_info = format(match.group(1))
                key = uuid.uuid4().hex
                tree['static']['vrf']['global'][key] = route_info

            elif context == 'port':

                if match(r'^ no (.*)', line):
                    key = format(match.group(1))
                    value = format(match.group(0)).lstrip()
                    tree['port'][portindex][key] = value

                # interface items are stored with helper class
                elif match('^ .*', line):
                    tree = port_parser.parse_line(tree, portindex, line)

                elif match(r'!$', line):
                    context = ''

            elif context == 'vlan':

                if match(r'^ name (.*)', line):
                    tree['vlan'][vlan]['name'] = format(match.group(1))

                elif line.startswith('!') or not line.startswith(''):
                    context = ''

        return tree
