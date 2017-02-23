class Person(object):
    def __init__(self):
        self.person_id = None
        self.name = None
        self.allocated_office_space = None
        self.num_of_people = None

    def get_name(self):
        pass

    def get_person_id(self):
        pass

    def get_allocated_office_space(self):
        pass

    def get_num_of_people(self):
        pass

class Staff(Person):
    def __init__(self):
        self.num_of_staff_members = None

    def get_num_of_staff_members(self):
        pass

class Fellow(Person):
    def __init__(self):
        self.num_of_fellows = None
        self.allocated_living_space = None

    def get_allocated_living_space(self):
        pass

    def get_num_of_fellows(self):
        pass

