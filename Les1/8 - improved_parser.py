import re
import json


class ReSearcher:
    match = None

    def __call__(self, pattern, string):
        self.match = re.search(pattern, string)
        return self.match

    def __getattr__(self, name):
        return getattr(self.match, name)


class Tree(dict):
    """ Autovivificious dictionary """
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

    def __str__(self):
        """ Serialize dictionary to JSON formatted string with indents """
        return json.dumps(self, indent=4)


def splitrange(raw_range):

    """
    '1,2,4-6' returns ['1','2','4','5','6']
    'none'    returns ['None']
    """

    m = re.search(r'^(\d+)\-(\d+)$', raw_range)
    if m:
        first = int(format(m.group(1)))
        last = int(format(m.group(2)))
        return [str(i) for i in range(first, last+1)]

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


def improved_parser(configfile):

    tree = Tree()
    match = ReSearcher()
    context = ''

    with open(configfile, 'r') as lines:
        
        for line in lines:

            line = line.rstrip()

            if match(r'hostname (.*)', line):
                hostname = format(match.group(1))
                tree['hostname'] = hostname

            elif match(r'^interface (.*)', line):
                portindex = format(match.group(1))
                context = 'port'
                allowed_vlans = []

            elif match(r'^vlan ([\d,-]+)', line):
                context = 'vlan'
                for vlan in splitrange(format(match.group(1))):
                    tree['vlan'][vlan] = {}

            elif context == 'port':

                if match(r'^ switchport mode (\w+)', line):
                    value = format(match.group(1))
                    tree['port'][portindex]['switchport mode'] = value

                elif match(r'^ description (.*)', line):
                    value = format(match.group(1))
                    tree['port'][portindex]['description'] = value

                elif match(r'^ switchport access vlan (\d+)', line):
                    value = format(match.group(1))
                    tree['port'][portindex]['switchport access vlan'] = value

                elif match(r'^ switchport trunk allowed vlan (add )?([0-9,-]+)', line):
                    value = format(match.group(2))
                    vlans = splitrange(value)
                    allowed_vlans.extend(vlans)
                    tree['port'][portindex]['vlans allowed'] = allowed_vlans
                    
                elif match(r'^ !', line):
                    context = ''

            elif context == 'vlan':
                
                if match(r'^ name (.*)', line):
                    tree['vlan'][vlan]['name'] = format(match.group(1))

                elif match(r'!', line):
                    context = ''

        return tree


def main():

    test = '1'

    configfiles = ['8 - Switch1-cfg.txt', '8 - Switch2-cfg.txt']

    trees = []
    for configfile in configfiles:
        trees.append(improved_parser(configfile))

    with open('8 - trees.json', 'w') as js:
        json.dump(trees, js, indent=4)


if __name__ == "__main__":
    main()
