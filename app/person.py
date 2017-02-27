class Person(object):
    def __init__(self, name):
        self.id = None
        self.name = name
        self.allocated_office_space = None

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
    
    def __init__(self, name):
        super(Staff, self).__init__(name)

class Fellow(Person):
    
    def __init__(self, name):
        super(Fellow, self).__init__(name)
        self.allocated_living_space = None

    def get_allocated_living_space(self):
        pass

    def set_allocated_living_space(self, room=None):
        pass

