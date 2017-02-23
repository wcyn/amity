class Room(object):
    def __init__(self):
        self.name = None
        self.max_occupants = None
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
    def __init__(self):
        self.num_of_office_spaces = None

    def get_num_of_office_spaces(self):
        pass

class LivingSpace(Room):
    def __init__(self):
        self.num_of_living_spaces = None

    def get_num_of_living_spaces(self):
        pass

