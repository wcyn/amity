class Person(object):
    def __init__(self, name, **kwargs):
        # If not defined, id is None
        self.id = kwargs.pop('id', None)
        self.name = name
        # If not defined, allocated_office_space is None
        self.allocated_office_space = kwargs.pop('allocated_office_space',
                                                 None)
    # Override the __new__() method
    def __new__(cls, *args, **kwargs):
        if cls is Person:
            raise TypeError("The Person class may not be instantiated")
        return super(Person, cls).__new__(cls)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def allocated_office_space(self):
        return self.__allocated_office_space

    @allocated_office_space.setter
    def allocated_office_space(self, allocated_office_space):
        self.__allocated_office_space = allocated_office_space

class Staff(Person):

    def __init__(self, *args):
        super(Staff, self).__init__(*args)


class Fellow(Person):

    def __init__(self, *args, **kwargs):
        super(Fellow, self).__init__(*args, **kwargs)
        # Default is None
        self.allocated_living_space = kwargs.pop('allocated_living_space',
         None)
        # Default is 'N', meaning No
        self.wants_accommodation = kwargs.pop('wants_accommodation', 'N')

    @property
    def allocated_living_space(self):
        return self.__allocated_living_space

    @allocated_living_space.setter
    def allocated_living_space(self, allocated_living_space):
        self.__allocated_living_space = allocated_living_space

    @property
    def wants_accommodation(self):
        return self.__wants_accommodation

    @wants_accommodation.setter
    def wants_accommodation(self, wants_accommodation):
        self.__wants_accommodation = wants_accommodation
