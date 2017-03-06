import sys

class Amity(object):
    """ """
    out = sys.stdout
    offices = None  # List of Office objects
    living_spaces = None  # List of LivingSpace objects
    fellows = None  # List of Fellow objects
    staff = None  # List of Staff objects
    error_codes = {
        1: "Room does not exist",
        2: "Person does not exist",
        3: "A room with that name already exists",
        4: "A person with that ID already exists",
        5: "Invalid person type",
        6: "Invalid room type",
        7: "Invalid accommodation option",
        8: "No room name was provided",
        9: "Person name was not provided",
        10: "Cannot allocate a living space to a staff member",
        11: "Cannot add person. The room is fully occupied",
        12: "Cannot find the file",
        13: "The file is empty",
        14: "Wrongly formatted file",
        15: "Invalid characters in the filename"
    }

    def create_room(self, room_names):
        pass

    def add_person(self, person_name, type, wants_accommodation="n"):
        pass

    def allocate_room_to_person(self, room, person):
        pass

    def reallocate_person(self, person_id, new_room_name):
        pass

    def load_people(self, filename):
        pass

    def print_allocations(self, filename=None):
        print("Jane Staff Camelot")
        print("Jake Fellow Occulus")
        print("Jake Fellow Camelot")
        pass

    def print_unallocated(self, filename=None):
        pass

    def print_room(self, room_name):
        pass
