import sys
import sqlite3

from .room import Office, LivingSpace
from .person import Staff, Fellow

class Amity(object):
    """ """
    out = sys.stdout
    offices = None  # List of Office objects
    living_spaces = None  # List of LivingSpace objects
    fellows = None  # List of Fellow objects
    staff = None  # List of Staff objects
    connection = None
    error_codes = {
        1: "Room does not exist",
        2: "Person does not exist",
        3: "Cannot create a duplicate room",
        4: "Cannot create a duplicate person",
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
        15: "Invalid characters in the filename",
        16: "The room is empty",
        17: "Invalid character(s) in the database name"
    }

    def create_room(self, room_names):
        new_rooms = []
        if not isinstance(room_names, list):
            return "Only a list of strings is allowed"
        if not len(room_names):
            return self.error_codes[8]
        room_names = set(room_names)
        for room_name in room_names:
            print("Room name: ", room_name)
            if room_name not in ([x.name for x in self.living_spaces] +
                                    [x.name for x in self.offices]):
                try:
                    if room_name[-3:] == "-ls":
                        print("Ls!")
                        new_living_space = LivingSpace(room_name[:-3])
                        self.living_spaces.append(new_living_space)
                        new_rooms.append(new_living_space)
                    else:
                        new_office = Office(room_name)
                        self.offices.append(new_office)
                        new_rooms.append(new_office)
                except TypeError as e:
                    raise(e)
                except Exception as e:
                    print(e)
                    raise(e)
            else:
                return self.error_codes[3] + " '%s'" % room_name
        return new_rooms

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

    def save_state(self, db="sqlite_database", override=False):
        self.connection = sqlite3.connect(db)
        pass
            # self.connection = "Nothing here"
            # try:
            #     self.connection = sqlite3.connect(db)
            #     return "connection succeeded"
            # except Exception as e:
            #     print("Error: ", e)
            #     return "connection failed"
            # finally:
            #     print("Conn: ", self.connection)
            # pass

            # a = Amity()
            # print(a.save_state("test_database/"))

