import re
import sys
import sqlite3
import random

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
            if not isinstance(room_name, str):
                raise TypeError

            if room_name.lower() not in ([x.name.lower() for x in self.living_spaces] +
                                    [x.name.lower() for x in self.offices]):
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

    def add_person(self, first_name, last_name, type, wants_accommodation=False):
        if not isinstance(wants_accommodation, bool):
            return self.error_codes[7] + " '%s'" % wants_accommodation
        try:
            new_person = None
            if type.lower() in self.allowed_fellow_strings:
                new_person = Fellow(first_name, last_name)
                self.fellows.append(new_person)
            elif type.lower() in self.allowed_staff_strings:
                new_person = Staff(first_name, last_name)
                self.staff.append(new_person)
            else:
                return self.error_codes[5] + " '%s'" % type

            # Randomly allocate office to new person
            self.randomly_allocate_room(new_person, self.allowed_office_strings[0])

            new_person.wants_accommodation = wants_accommodation
            if wants_accommodation:
                # Randomly assign available living space to fellow
                result = self.randomly_allocate_room(new_person, self.allowed_living_space_strings[0])
                if result:
                    # Reset wants accommodation to False since they now have accommodation
                    new_person.wants_accommodation = False

            return new_person

        except TypeError as e:
            raise (e)
        except Exception as e:
            print(e)
            raise (e)

    def allocate_room_to_person(self, person, room, reallocate=False):
        try:
            if room.get_max_occupants() - room.num_of_occupants:
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
            return person
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e

    def randomly_allocate_room(self, person, room_type):
        if room_type not in self.allowed_living_space_strings + self.allowed_office_strings:
            return self.error_codes[6] + " '%s'" % room_type

        offices_not_full = [office for office in self.offices if office.get_max_occupants() - office.num_of_occupants]
        living_spaces_not_full = [living_space for living_space in self.living_spaces
                                  if living_space.get_max_occupants() - living_space.num_of_occupants]

        data = None
        if room_type in self.allowed_office_strings:
            if offices_not_full:
                # Randomly select an non full office
                office = random.choice(offices_not_full)
                self.allocate_room_to_person(person, office)
                data = office
        else:
            if living_spaces_not_full:
                # Randomly select a non full living space
                living_space = random.choice(living_spaces_not_full)
                self.allocate_room_to_person(person, living_space)
                data = living_space
        return data

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
            return loaded_people

        except FileNotFoundError as e:
            return self.error_codes[12] + " '%s'" % filename
        except TypeError as e:
            raise TypeError
        except Exception as e:
            raise e

    def print_allocations(self, filename=None):
        try:
            staff = [' '.join((i.first_name, i.last_name, "Staff", i.allocated_office_space.name, '\n'))
                     for i in self.staff if i.allocated_office_space]
            fellows_allocated_both = [' '.join((i.first_name, i.last_name, "Fellow", i.allocated_office_space.name,
                                 i.allocated_living_space.name, '\n'))
                       for i in self.fellows if i.allocated_living_space and i.allocated_office_space]
            fellows_with_only_living_space = [' '.join((i.first_name, i.last_name, "Fellow", "-",
                                                        i.allocated_living_space.name, '\n'))
                                              for i in self.fellows if
                                              i.allocated_living_space and not i.allocated_office_space]
            fellows_with_only_office_space = [' '.join((i.first_name, i.last_name, "Fellow",
                                                        i.allocated_office_space.name, "-", '\n'))
                                              for i in self.fellows if
                                              not i.allocated_living_space and i.allocated_office_space]
            fellows = fellows_allocated_both + fellows_with_only_living_space + fellows_with_only_office_space
            allocations = staff + fellows
            message = None
            if not allocations:
                message = "No allocations to print"


            if filename:
                if not isinstance(filename, str):
                    raise TypeError
                # Clean filename. Remove unwanted filename characters
                filename = ''.join(x for x in filename if x not in "\/:*?<>|")
                with open(filename, 'w') as f:
                    f.writelines(allocations)
            else:
                for allocation in allocations:
                    print(allocation.strip())
            return {"filename": filename, "allocations": allocations, "message": message}
        except Exception as e:
            raise e

    def print_unallocated(self, filename=None):
        try:
            staff = [' '.join((i.first_name, i.last_name, "Staff", '\n'))
                     for i in self.staff if not i.allocated_office_space]
            fellows_with_neither_allocations = [' '.join((i.first_name, i.last_name, "Fellow", '\n'))
                       for i in self.fellows if not i.allocated_living_space and not i.allocated_office_space]
            fellows_with_only_living_space = [' '.join((i.first_name, i.last_name, "Fellow", "-",
                                                i.allocated_living_space.name, '\n'))
                       for i in self.fellows if i.allocated_living_space and not i.allocated_office_space]
            fellows_with_only_office_space = [' '.join((i.first_name, i.last_name, "Fellow",
                                                        i.allocated_office_space.name, "-", '\n'))
                       for i in self.fellows if not i.allocated_living_space and i.allocated_office_space
                                              and i.wants_accommodation]
            fellows = fellows_with_neither_allocations + fellows_with_only_living_space + fellows_with_only_office_space

            unallocated = staff + fellows
            message = None
            if not unallocated:
                message = "No unallocated to print"

            if filename:
                if not isinstance(filename, str):
                    raise TypeError
                # Clean filename. Remove unwanted filename characters
                filename = ''.join(x for x in filename if x not in "\/:*?<>|")
                with open(filename, 'w') as f:
                    f.writelines(unallocated)
            else:
                for allocation in unallocated:
                    print(allocation.strip())
            return {"filename": filename, "unallocated": unallocated, "message": message}
        except Exception as e:
            raise e


    def print_room(self, room_name):
        if not isinstance(room_name, str):
            raise TypeError
        rooms = [room for room in self.offices + self.living_spaces]
        # allocated_rooms = [person.allocated_office_space + pers for person in people]
        room_name = room_name.lower()
        people_count = 0
        if rooms:
            if room_name in [room.name.lower() for room in rooms]:
                for staff in self.staff:
                    if staff.allocated_office_space:
                        if room_name == staff.allocated_office_space.name.lower():
                            print("%s %s %s" % (staff.first_name, staff.last_name, "Staff"))
                            people_count += 1
                for fellow in self.fellows:
                    if fellow.allocated_office_space:
                        if room_name == fellow.allocated_office_space.name.lower():
                            print("%s %s %s" % (fellow.first_name, fellow.last_name, "Fellow"))
                            people_count += 1
                    elif fellow.allocated_living_space:
                        if room_name == fellow.allocated_living_space.name.lower():
                            print("%s %s %s" % (fellow.first_name, fellow.last_name, "Fellow"))
                            people_count += 1

                if not people_count:
                    # Room is empty
                    return self.error_codes[16] + ": '%s'" %room_name
            else:
                # Room does not exist
                return self.error_codes[1] + ": '%s'" % room_name
        else:
            return "There are no rooms yet"

        return people_count
        


    def save_state(self, db_name="sqlite_database", override=False):
        try:
            if set('[~!@#$%^&*()+{}"/\\:;\']+$').intersection(db_name):
                return self.error_codes[17] + " '%s'" % db_name

            db_file = self.database_directory + db_name
            db_path = Path(db_file)
            if db_path.is_file() and not override:
                return "About to override database '%s'" % db_name

            if not self.offices + self.living_spaces  + self.fellows + self.staff:
                return "No data to save"

            print("Connecting now..")
            self.connection = sqlite3.connect(db_file)
            # if self.connection.fetchone():
            #     return "connection succeeded"
            # else:
            #     return "connection failed"
            return self.connection
        except Exception as e:
            print("Error: ", e)
            raise(e)
        finally:
            print("Conn: ", self.connection)
            # return self.connection

    def load_state(self, db_name):
        pass

