import json


def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)

    for tree in trees:
        if 'Switch' not in tree['hostname']:
            continue
        for port, portitems in tree['port'].items():
            if (portitems.get('switchport mode') == 'access' and
                    portitems.get('spanning-tree portfast') != 'spanning-tree portfast'):
                fmt = 'Design validation detected on switch {} and port {}'
                print(fmt.format(tree['hostname'], port))
       
if __name__ == "__main__":
    main()
