class Person(object):
    def __init__(self, name, allocated_office_space):
        self.id = None
        self.name = name
        self.allocated_office_space = allocated_office_space
        self.num_of_people = None

    def get_name(self):
        pass

    def get_person_id(self):
        pass

    def get_allocated_office_space(self):
        pass

    def get_num_of_people(self):
        pass

    def set_person_id(self, id):
        self.id = id

class Staff(Person):
        num_of_staff_members = None

    def get_num_of_staff_members(self):
        pass

class Fellow(Person):
    
    num_of_fellows = None
    allocated_living_space = None

    def get_allocated_living_space(self):
        pass

    def get_num_of_fellows(self):
        pass

    def set_allocated_living_space(self, room=None):
        pass

