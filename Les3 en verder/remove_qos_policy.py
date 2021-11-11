import json
from collections import defaultdict


def get_tree_by_hostname(trees, hostname):

    for tree in trees:
        if tree['hostname'] == hostname:
            return tree


def main():

    # First run parser script so that JSON file is read from disk
    with open('trees.json', 'r') as file:
        trees = json.load(file)

    tree = get_tree_by_hostname(trees, 'Router1')

    # Create class-map to ACL mappings and policy-map to class-map mappings
    class_map_to_acl_mapping = {}
    policy_map_to_class_map_mapping = defaultdict(list)
    cmaps = set()
    acls = set()
    pmaps = set()
    for hierarc_item in tree['hierarc_cfgs']:
        if hierarc_item[0].startswith('class-map'):
            cmaps.add(hierarc_item[0].split()[1])
            for line in hierarc_item:
                if line.startswith(' match access-group'):
                    class_map_to_acl_mapping[hierarc_item[0].split()[1]] = \
                        line.split()[-1]
                    acls.add(line.split()[-1])
        elif hierarc_item[0].startswith('policy-map'):
            pmap = hierarc_item[0].split()[-1]
            pmaps.add(pmap)
            for line in hierarc_item:
                if line.startswith(' class'):
                    class_ = line.split()[1]
                    policy_map_to_class_map_mapping[pmap].append(class_)

    print(policy_map_to_class_map_mapping)
    print(class_map_to_acl_mapping)
            

     # Create interface to policy-map mappings
    port_input_pmap_mapping = {}
    port_output_pmap_mapping = {}
    for port, portitems in tree['port'].items():
        if portitems.get('service-policy input') is not None:
            port_input_pmap_mapping[port] = portitems['service-policy input']
        elif portitems.get('service-policy output') is not None:
            port_input_pmap_mapping[port] = portitems['service-policy output']

    print(port_input_pmap_mapping)

    # Remove QoS policies
    for port in port_input_pmap_mapping:
        print(port)
        print(' no service-policy input {}'.format(port_input_pmap_mapping[port]))

    for pmap in policy_map_to_class_map_mapping:
        print(pmap)
        for class_ in policy_map_to_class_map_mapping[pmap]:
            print(' no class {}'.format(class_))

    for cmap in class_map_to_acl_mapping:
        print('class-map ' + cmap)
        print(' no match access-group {}'.format(class_map_to_acl_mapping[cmap]))

    for pmap in pmaps:
        print('no policy-map ' + pmap)
    for cmap in cmaps:
        print('no class-map ' + cmap)
    for acl in acls:
        print('no access-list ' + acl)
    
    


        
                
        
        
            



        
        

    

    

    
    
        
   



    

   

if __name__ == "__main__":
    main()
