class Room(object):
    def __init__(self, name):
        self.name = name
        self.num_of_occupants = None

    def __new__(cls, *args, **kwargs):
        if cls is Room:
            raise TypeError("The Room class may not be instantiated")
        return super(Room, cls).__new__(cls)
        
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name.islower() and name.istitle():
            self.__name = ''.join(name.split()).title()
        else:
            self.__name = ''.join(name.split())

    @property
    def num_of_occupants(self):
        return self.__num_of_occupants

    @num_of_occupants.setter
    def num_of_occupants(self, num_of_occupants):
            self.__num_of_occupants = num_of_occupants

    def get_max_occupants(self):
        return self.max_occupants

class Office(Room):
    max_occupants = 6

class LivingSpace(Room):
    max_occupants = 4   

