class Room(object):
    def __init__(self, name):
        self.name = name
        self.num_of_occupants = None

    def __new__(cls, *args, **kwargs):
        if cls is Room:
            raise TypeError("The Room class may not be instantiated")
        return super(Room, cls).__new__(cls)
        
    def get_name(self):
        pass

    def get_max_occupants(self):
        return self.max_occupants

    def get_num_of_occupants(self):
        pass


class Office(Room):
    def __init__(self, name):
        super(Office, self).__init__(name)
        self.max_occupants = 6

    def get_num_of_office_spaces(self):
        pass

class LivingSpace(Room):
    def __init__(self, name):
        super(Office, self).__init__(name)
        self.max_occupants = 4

    def get_num_of_living_spaces(self):
        pass

