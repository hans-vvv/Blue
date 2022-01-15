from pol_utils import reversed_dict_iter


class StackMember:

    """
    Class representing a single stack member.
    """

    def __init__(self, model, uplinkmodule=None):
        self.model = model
        self.uplinkmodule = uplinkmodule


class Stack:

    """
    Class representing a set of stack members. This class enables the backbone
    creation of a site with multiple stacks using auto assignment of NNI
    (Network To Network) interfaces of the individual stacks. Also methods are
    available to return lists of the available UNI (User to Network) and NNI
    interfaces.
    """

    def __init__(self, devicerole):
        self.devicerole = devicerole  # router or switch
        self.sequence_number = 1
        self.stackconfig = {}

    def add_stackmember(self, stackmember):
        """
        Enables adding a stack member into a stack. Several instance attributes
        are created. The most important is a dict with port index = key and 
        tuple containing remote element and remote port as value; this is used
        to track reservations made to create the backbone. Also a list of all
        available NNI ports is created.

        :param stackmember: object of StackMember class.
        :return: None
        """

        self.stackconfig[self.sequence_number] = stackmember
        self.sequence_number += 1

        self.nni_port_list = self.get_nni_port_list()
        self.nni_port_assignment = {}
        for port in self.nni_port_list:
            self.nni_port_assignment[port] = ('', '')

        self.slots = self._get_nni_slots()

    def get_uni_port_list(self):

        """
        This method returns a list of all available UNI ports of a stack.

        :return: list of available UNI ports
        """
        uni_port_list = []
        fmt1 = 'GigabitEthernet2/{}'
        for sequence_number, stackmember in self.stackconfig.items():
            if '4P' in stackmember.model:
                for i in range(0, 4):
                    uni_port_list.append(fmt1.format(i))
            
        return uni_port_list

    def get_nni_port_list(self):
        """
        This method returns a list of all available NNI ports of a stack.

        :return: List of all available NNI ports.
        """
        nni_port_list = []
        fmt1 = 'GigabitEthernet0/{}'
        fmt2 = 'GigabitEthernet1/{}'
        for sequence_number, stackmember in self.stackconfig.items():
            if 'NM-8X' in stackmember.uplinkmodule:
                for i in range(0, 4):
                    nni_port_list.append(fmt1.format(i))
                for i in range(0, 4):
                    nni_port_list.append(fmt2.format(i))
            
        return nni_port_list

    def _get_nni_slots(self):
        """
        Private method which returns list of available uplink modules

        :return: list of available uplink modules
        """
        slots = []
        for sequence_number, stackmember in self.stackconfig.items():
            if 'NM-8X' in stackmember.uplinkmodule:
                slots.append('NM-8X')
        return slots

    def reserve_nni_port(self, port):
        """
        The NNI port reservation is updated to indicate that this port
        cannot be used to form the backbone.

        :param port: NNI interface from stack
        :return: None
        """
        self.nni_port_assignment[port] = ('reserved', 'reserved')


    def _get_free_nni_ports(self, slot):
        """
        Private method which returns the number of free NNI ports from a
        given slot

        :param slot: integer representing the slot containing NNI interfaces.
        :return: Integer number of free ports.
        """
        port_count = 0
        for port in self.nni_port_assignment:
            if self.nni_port_assignment[port] == ('', ''):
                port_count += 1
        return port_count

    def auto_assign_nni_port(self, devicename, order='reverse'):
        """
        This method assigns a free NNI port in the creation process of a site
        backbone. Ports can be assigned from 'left to right' with keyword
        order='fwd' or from 'right to left' which is default. NNI port
        reservation instance attribute is updated.

        :param devicename: name of remote device to connect to the stack
        :param order: see docstring
        :return: None
        """

        if len(self.slots) == 1:
            iterable = reversed_dict_iter(self.nni_port_assignment) \
                if order == 'reverse' else self.nni_port_assignment
            for port in iterable:
                if self.nni_port_assignment[port] == ('', ''):
                    self.nni_port_assignment[port] = (devicename, '')
                    break

        elif len(self.slots) == 2:
            iterable = reversed_dict_iter(self.nni_port_assignment) \
                if order == 'reverse' else self.nni_port_assignment
            if self._get_free_nni_ports(1) >= self._get_free_nni_ports(2):
                slot = '1/'
            else:
                slot = '2/'
            for port in iterable:
                if not ('net' + slot) in port:
                    continue
                if self.nni_port_assignment[port] == ('', ''):
                    self.nni_port_assignment[port] = (devicename, '')
                    break

    def reserve_ports_for(self, remote_device):
        """
        This method returns a list of interfaces device for which reservations
        have been made given the name of the remote device.

        :param remote_device: hostname of remote device
        :return: list of NNI interfaces
        """
        local_ports = [port for port in self.nni_port_assignment
                       if self.nni_port_assignment[port][0] == remote_device]
        return local_ports

    def connect_devices(self, port, remote_port):
        """
        The NNI reservation instance attribute is updated when the remote
        interface is assigned.
        :param port: Local port
        :param remote_port: Remote port
        :return: None
        """
        remote_device = self.nni_port_assignment[port][0]
        self.nni_port_assignment[port] = (remote_device, remote_port)


if __name__ == '__main__':

    stack = Stack('router')
    stackmember = StackMember('c9300-4P', 'NM-8X')
    stack.add_stackmember(stackmember)
    
    print(stack.get_uni_port_list())
    print(stack.get_nni_port_list())
