
class Amity(object):

    offices = None # List of Office objects
    living_spaces = None # List of LivingSpace objects
    fellows = None # List of Fellow objects
    staff = None # List of Staff objects

    def create_room(self, room_names):
        pass

    def add_person(self, person_name, type, wants_accomodation="n"):
        pass

    def allocate_room_to_person(room, person):
        pass

    def reallocate_person(self, person_id, new_room_name):
        pass

    def load_people(self, filename):
        pass

    def print_allocations(self, filename):
        pass

    def print_unallocated(self, filename):
        pass

    def print_room(self, room_name):
        pass
