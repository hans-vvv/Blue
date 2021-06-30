import json


def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)

    tree = get_tree_by_hostname(trees, 'Router2')
    result = []

    for port in tree['port'].keys():
        if 'Vlan' in port:
            result.append(port)

    print(result)

    
        
   



    

   

if __name__ == "__main__":
    main()
