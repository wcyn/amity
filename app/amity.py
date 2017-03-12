import re
import sys
import sqlite3

from app.room import Office, LivingSpace
from app.person import Staff, Fellow
from pathlib import Path


class Amity(object):
    """ """
    out = sys.stdout
    offices = None  # List of Office objects
    living_spaces = None  # List of LivingSpace objects
    fellows = None  # List of Fellow objects
    staff = None  # List of Staff objects
    connection = None
    database_directory = "../databases/"
    files_directory = "../files/"
    allowed_fellow_strings = ["fellow", "f"]
    allowed_staff_strings = ["staff", "s"]
    allowed_office_strings = ["office", "o"]
    allowed_living_space_strings = ["living_space", "ls"]
    allowed_yes_strings= ["yes", "y"]
    allowed_no_strings = ["no", "n"]
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

    def add_person(self, first_name, last_name, type, wants_accommodation="n"):
        new_person = None
        try:
            if type.lower() in self.allowed_fellow_strings:
                print("Fellow!")
                new_person = Fellow(first_name, last_name)
                self.fellows.append(new_person)
            elif type.lower() in self.allowed_staff_strings:
                new_person = Staff(first_name, last_name)
                self.staff.append(new_person)
            else:
                return self.error_codes[5] + " '%s'" % type

            if wants_accommodation.lower() in self.allowed_yes_strings:
                pass
            elif wants_accommodation.lower() in self.allowed_no_strings:
                pass
            else:
                return self.error_codes[7] + " '%s'" % wants_accommodation

        except TypeError as e:
            raise (e)
        except Exception as e:
            print(e)
            raise (e)

        return new_person

    def allocate_room_to_person(self, person, room, reallocate=False):
        try:
            if (room.get_max_occupants() - room.num_of_occupants):
                # Should not assign a living space to a staff member
                if isinstance(person, Staff) and isinstance(room, LivingSpace):
                    return self.error_codes[10]

                already_allocated_office = isinstance(room, Office) and isinstance(
                    person.allocated_office_space, Office)
                already_allocated_living_space = isinstance(room, LivingSpace) and isinstance(
                    person.allocated_living_space, LivingSpace)

                if not reallocate:
                    if already_allocated_office:
                        # Person already has office space
                        return "About to move %s from %s to %s" %(person.first_name,
                                                                  person.allocated_office_space.name, room.name)
                    elif already_allocated_living_space:
                        # Person already has office space
                        return "About to move %s from %s to %s" %(person.first_name,
                                                              person.allocated_living_space.name, room.name)
                if isinstance(room, Office):
                    person.allocated_office_space = room
                elif isinstance(room, LivingSpace):
                    person.allocated_living_space = room
            else:
                return self.error_codes[11]
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e
        return person

    def load_people(self, filename):
        try:
            with open(filename) as f:
                people = f.readlines()
            if not len(" ".join([i.strip() for i in people])):
                return self.error_codes[13] + " '%s'" % filename

            loaded_people = []
            for i in people:
                # match the required formatting for each line
                if re.match('^(\w+\s\w+\s(FELLOW|STAFF|F|S)(\s(YES|Y|NO|N))?)$',i.strip(), re.IGNORECASE):
                    # proceed to create the objects else ignore the bad line
                    person_data = i.strip().split()
                    if person_data[2].lower() in self.allowed_fellow_strings:
                        fellow = Fellow(person_data[0], person_data[1])
                        self.fellows.append(fellow)
                        loaded_people.append(fellow)
                    else:
                        staff = Staff(person_data[0], person_data[1])
                        self.staff.append(staff)
                        loaded_people.append(staff)
                else:
                    print("Ignoring badly formatted line: ", i.strip())

            if not loaded_people:
                # None of the lines had the required format
                return self.error_codes[14] + " '%s'" % filename


        except FileNotFoundError as e:
            return self.error_codes[12] + " '%s'" % filename
        except TypeError as e:
            raise TypeError
        except Exception as e:
            raise e

    def print_allocations(self, filename=None):
        print("Jane Staff Camelot")
        print("Jake Fellow Occulus")
        print("Jake Fellow Camelot")
        pass

    def print_unallocated(self, filename=None):
        pass

    def print_room(self, room_name):
        pass

    def save_state(self, db_name="sqlite_database", override=False):
        try:
            if set('[~!@#$%^&*()+{}"/\\:;\']+$').intersection(db_name):
                return self.error_codes[17] + " '%s'" % db_name

            db_file = self.database_directory + db_name
            db_path = Path(db_file)
            if db_path.is_file():
                return "About to override database '%s'" % db_name

            if not (self.offices + self.living_spaces  + self.fellows + self.staff):
                return "No data to save"

            self.connection = sqlite3.connect(db_file)
            return "connection succeeded"
        except Exception as e:
            print("Error: ", e)
            raise(e)
        finally:
            print("Conn: ", self.connection)
        pass

    def load_state(self, db_name):
        pass

