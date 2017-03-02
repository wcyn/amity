class Person(object):
    def __init__(self, name, **kwargs):
        self.id = id
        self.name = name
        # If not defined, id is None
        self.id = kwargs.pop('id', None)
        # If not defined, allocated_office_space is None
        self.allocated_office_space = kwargs.pop('allocated_office_space',
                                                 None)
    # Override the __new__() method
    def __new__(cls, *args, **kwargs):
        if cls is Person:
            raise TypeError("The Person class may not be instantiated")
        return super(Person, cls).__new__(cls)

    def get_id(self):
        pass

    def get_name(self):
        pass

    def get_person_id(self):
        pass

    def get_allocated_office_space(self):
        pass

    def set_id(self, id):
        pass

    def set_name(self):
        pass

    def set_allocated_office_space(self, allocated_office_space):
        pass


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



    def get_allocated_living_space(self):
        pass

    def get_wants_accommodation(self):
        pass

    def set_allocated_living_space(self, room=None):
        pass

    def set_wants_accommodation(self, room=None):
        pass

