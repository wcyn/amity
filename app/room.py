class Room(object):
    def __init__(self, name):
        self.name = name
        self.num_of_occupants = None
        self.num_of_rooms = None

    def get_name(self):
        pass

    def get_max_occupants(self):
        pass

    def get_num_of_occupants(self):
        pass

    def get_num_of_rooms(self):
        pass

class Office(Room):
    def __init__(self, name):
        super(Office, self).__init__(name)
        self.max_occupants = 6

    def get_num_of_office_spaces(self):
        pass

class LivingSpace(Room):
    def __init__(self, namea):
        super(Office, self).__init__(name)
        self.max_occupants = 4

    def get_num_of_living_spaces(self):
        pass

