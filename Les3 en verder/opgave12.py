## What you could do is the following:
## For each SVI interface you can create a mapping between interface
## and priority, so in this case Vlan3 --> 254.
## The dictionary data structure is a good candidate to do this.
## So you need to create the mappings for both Router1 and Router2


##        "port": {
##            "Vlan3": {
##                "description": "Voice",
##                "ip vrf forwarding": "4",
##                "ip address": [
##                    "10.0.0.1 255.255.255.0"
##                ],
##                "standby": [
##                    "1 ip 10.0.0.254",
##                    "1 priority 254"
##                ],
##                "ip helper-address": [
##                    "10.1.0.1",
##                    "10.1.0.2"


## After you have create both dictionaries you can loop over the dictionary
## of Router1. Then you can create another inner loop of Router2. If both
## interfaces matches you can determine if the priorities matches the design
## rules. Time for an example:

port_hrsp_prio_router1 = {'Vlan3': '254', 'Vlan4': '100'}
port_hrsp_prio_router2 = {'Vlan3': '100', 'Vlan4': '254'}

for port1 in port_hrsp_prio_router1: # shortcut, I Don't use keys() method here
    for port2 in port_hrsp_prio_router2:
        if port1 == port2:
            if int(hrsp_prio_router1[port1]) <= int(hrsp_prio_router2[port2]):
                print('Design validation detected on port {}'.format(port1))


        

