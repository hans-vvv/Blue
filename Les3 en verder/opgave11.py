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

    vlan_db = set()
    for vlan in tree['vlan'].keys():
        # Prepend 'Vlan' in order to compare with SVI interfaces (svi_ports)
        vlan_db.add('Vlan' + vlan) 

    #print(vlan_db)


    svi_ports = set()
    for port in tree['port'].keys():
        if 'Vlan' not in port:
            continue
        svi_ports.add(port)

    #print(svi_ports)

    result = svi_ports - vlan_db

    print(result)



        
        

    

    

    
    
        
   



    

   

if __name__ == "__main__":
    main()
