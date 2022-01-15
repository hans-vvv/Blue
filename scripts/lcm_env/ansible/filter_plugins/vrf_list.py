class FilterModule:

    def filters(self):
        return {
            'ios_vrf_list': self.ios_vrf_list
        }

    def ios_vrf_list(self, registered_data):

        vrf_list = []
        
        for line in registered_data['stdout_lines'][0]:

            if 'interfaces' in line.lower() or len(line.split()) !=4:
                continue
            vrf_list.append(line.split()[0])

        return vrf_list





