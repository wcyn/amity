from abc import ABCMeta, abstractmethod


class Room(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, name):
        self.name = name
        self.num_of_occupants = 0

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name.islower() or not name.isupper():
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

    def __init__(self, name):
        super(Office, self).__init__(name)


class LivingSpace(Room):
    max_occupants = 4

    def __init__(self, name):
        super(LivingSpace, self).__init__(name)
