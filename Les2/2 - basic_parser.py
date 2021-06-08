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


def basic_parser(configfile):

    tree = Tree()
    match = ReSearcher()
    context = ''

    with open(configfile, 'r') as lines:
        
        for line in lines:

            if match(r'hostname (.*)', line):
                hostname = format(match.group(1))
                tree['hostname'] = hostname

            elif match(r'^interface (.*)', line):
                context = 'port'
                portindex = format(match.group(1))

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

                elif match(r'^ switchport trunk allowed vlan (\d+)', line):
                    value = format(match.group(1))
                    tree['port'][portindex]['switchport trunk allowed vlan'] = value

                elif match(r'^ !', line):
                    context = ''

        return tree


def main():

    configfiles = ['2 - Switch1-cfg.txt']

    trees = []
    for configfile in configfiles:
        trees.append(basic_parser(configfile))

    with open('2 - trees.json', 'w') as js:
        json.dump(trees, js, indent=4)


if __name__ == "__main__":
    main()
