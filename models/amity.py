import re
import sqlite3
import random

from pathlib import Path

from termcolor import cprint, colored

from models.config import Config
from models.room import LivingSpace, Office, Room
from models.person import Staff, Fellow


class Amity(object):
    offices = []  # List of Office objects
    living_spaces = []  # List of LivingSpace objects
    fellows = []  # List of Fellow objects
    staff = []  # List of Staff objects

    def create_room(self, room_names, room_type='office'):

        """

        :param room_names:
        :type room_names:
        :param room_type:
        :type room_type:
        :return:
        :rtype:
        """
        new_rooms = []
        if not isinstance(room_names, list):
            return "Only a list of strings is allowed"
        if not len(room_names):
            return Config.error_codes[8]

        room_names = set(room_names)
        for room_name in room_names:
            if not isinstance(room_name, str):
                raise TypeError
            if room_name.lower() not in ([room.name.lower() for room in
                                          self.get_all_rooms()]):
                try:
                    if room_type in Config.allowed_living_space_strings:
                        new_living_space = LivingSpace(room_name)
                        self.living_spaces.append(new_living_space)
                        new_rooms.append(new_living_space)
                    else:
                        new_office = Office(room_name)
                        self.offices.append(new_office)
                        new_rooms.append(new_office)
                except TypeError as e:
                    raise e
                except Exception as e:
                    self.print_info(e)
                    raise e
            else:
                return Config.error_codes[3] + " '%s'" % room_name
        return new_rooms

    def add_person(self, first_name, last_name, role,
                   wants_accommodation=False):
        """

        :param first_name:
        :type first_name:
        :param last_name:
        :type last_name:
        :param role:
        :type role:
        :param wants_accommodation:
        :type wants_accommodation:
        :return:
        :rtype:
        """
        if not isinstance(wants_accommodation, bool):
            return Config.error_codes[7] + " '%s'" % wants_accommodation
        try:
            if role.lower() in Config.allowed_fellow_strings:
                new_person = Fellow(first_name, last_name)
                new_person.wants_accommodation = wants_accommodation
                self.fellows.append(new_person)

            elif role.lower() in Config.allowed_staff_strings:
                new_person = Staff(first_name, last_name)
                self.staff.append(new_person)
            else:
                return Config.error_codes[5] + " '%s'" % role
            # Randomly allocate office to new person
            if not self.offices:
                self.print_info("There exists no offices to assign to "
                                "'%s %s'" % (new_person.first_name,
                                             new_person.last_name))
            else:
                room = self.randomly_allocate_room(
                    new_person, Config.allowed_office_strings[0])
                if room:
                    self.print_info("Randomly allocating office to %s..." %
                                    new_person.first_name)
                    # time.sleep(1)
                    self.print_info_result("Allocated office: %s" % room.name)
                else:
                    self.print_info("All offices are full. No office to "
                                    "assign to '%s %s'" %
                                    (new_person.first_name,
                                     new_person.last_name))

            if wants_accommodation:
                if role.lower() in Config.allowed_fellow_strings:
                    # Randomly assign available living space to fellow
                    if not self.living_spaces:
                        self.print_info(
                            "There exists no living space to assign "
                            "fellow to")
                    else:
                        self.print_info("Randomly allocating living space to "
                                        "%s..." % new_person.first_name)
                        # time.sleep(1)
                        room = self.randomly_allocate_room(
                            new_person,
                            Config.allowed_living_space_strings[0])

                        if room:
                            self.print_info_result(
                                "Allocated living space: %s" % room.name)
                            # Reset wants accommodation to False since they now
                            # have accommodation
                            new_person.wants_accommodation = False
                        else:
                            self.print_info(
                                "All living spaces are full. No living space "
                                "to assign to '%s %s'" %
                                (new_person.first_name, new_person.last_name))
                else:
                    self.print_error(Config.error_codes[10])
            return new_person

        except TypeError as error:
            raise error
        except Exception as error:
            self.print_info(error)
            raise error

    @staticmethod
    def allocate_room_to_person(person, room, reallocate=False):
        """

        :param person:
        :type person:
        :param room:
        :type room:
        :param reallocate:
        :type reallocate:
        :return:
        :rtype:
        """
        print("room '%s' and person '%s' allocate room to person" % (room,
                                                                     person))
        try:
            if room.get_max_occupants() - room.num_of_occupants:
                # Should not assign a living space to a staff member
                if isinstance(person, Staff) and isinstance(room, LivingSpace):
                    return Config.error_codes[10]

                already_allocated_office = isinstance(
                        room, Office) and isinstance(
                    person.allocated_office_space, Office)
                already_allocated_living_space = isinstance(
                        room, LivingSpace) and isinstance(
                    person.allocated_living_space, LivingSpace)

                if not reallocate:
                    if already_allocated_office:
                        # Person already has office space
                        return "About to move %s from %s to %s" % (
                            person.first_name,
                            person.allocated_office_space.name, room.name)
                    elif already_allocated_living_space:
                        # Person already has office space
                        return "About to move %s from %s to %s" % (
                            person.first_name,
                            person.allocated_living_space.name, room.name)

                if isinstance(room, Office):
                    person.allocated_office_space = room
                elif isinstance(room, LivingSpace):
                    person.allocated_living_space = room

            else:
                return Config.error_codes[11]
            return person
        except AttributeError as e:
            raise e

    def randomly_allocate_room(self, person, room_type):
        """

        :param person:
        :type person:
        :param room_type:
        :type room_type:
        :return:
        :rtype:
        """
        if room_type not in Config.allowed_living_space_strings + \
                Config.allowed_office_strings:
            return Config.error_codes[6] + " '%s'" % room_type

        offices_not_full = [office for office in self.offices
                            if office.get_max_occupants() -
                            office.num_of_occupants]
        living_spaces_not_full = [living_space for living_space in
                                  self.living_spaces
                                  if living_space.get_max_occupants() -
                                  living_space.num_of_occupants]

        data = None
        if room_type in Config.allowed_office_strings:
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
        """
        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        try:
            with open(filename) as f:
                people = f.readlines()
            if not len(" ".join([i.strip() for i in people])):
                return Config.error_codes[13] + " '%s'" % filename

            loaded_people = []
            for person in people:
                # match the required formatting for each line
                if re.match('^(\w+\s\w+\s(FELLOW|STAFF|F|S)'
                            '(\s(YES|Y|NO|N))?)$', person.strip(),
                            re.IGNORECASE):
                    # proceed to create the objects else ignore the bad line
                    person_data = person.strip().split()
                    if person_data[2].lower() in Config.allowed_fellow_strings:
                        fellow = self.add_person(
                                person_data[0], person_data[1],
                                Config.allowed_fellow_strings[0])
                        loaded_people.append(fellow)
                    elif person_data[2].lower() in \
                            Config.allowed_staff_strings:
                        staff = self.add_person(
                                person_data[0],
                                person_data[1],
                                Config.allowed_staff_strings[0])
                        loaded_people.append(staff)
                else:
                    self.print_info("Ignoring badly formatted line: %s " %
                                    person.strip())

            if not loaded_people:
                # None of the lines had the required format
                return Config.error_codes[14] + " '%s'" % filename
            return loaded_people

        except FileNotFoundError:
            return Config.error_codes[12] + " '%s'" % filename
        except TypeError as error:
            raise error

    def print_allocations(self, filename=None):
        """

        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        try:
            allocated_staff = self.get_allocated_staff()

            fellows_allocated_both = self.get_fellows_allocated_both()
            fellows_with_only_living_space = \
                self.get_fellows_with_living_space_only()
            fellows_with_only_office_space = \
                self.get_fellows_with_office_space_only()
            allocated_fellows = fellows_allocated_both \
                + fellows_with_only_living_space \
                + fellows_with_only_office_space
            allocations = allocated_staff + allocated_fellows
            if not allocations:
                return "No allocations to print"

            allocated_staff_print = [' '.join(
                    (staff.first_name, staff.last_name, "Staff",
                     staff.allocated_office_space.name, '\n'))
                    for staff in allocated_staff]
            fellows_allocated_both_print = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow",
                     fellow.allocated_office_space.name,
                     fellow.allocated_living_space.name, '\n'))
                     for fellow in fellows_allocated_both]
            fellows_with_only_living_space_print = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow", "-",
                     fellow.allocated_living_space.name, '\n'))
                     for fellow in fellows_with_only_living_space]
            fellows_with_only_office_space_print = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow",
                     fellow.allocated_office_space.name, "-", '\n'))
                     for fellow in fellows_with_only_office_space]

            allocations_print = allocated_staff_print\
                + fellows_allocated_both_print \
                + fellows_with_only_living_space_print \
                + fellows_with_only_office_space_print
            if filename:
                if not isinstance(filename, str):
                    raise TypeError
                # Clean filename. Remove unwanted filename characters
                filename = ''.join(x for x in filename if x not in "\/:*?<>|")
                with open(filename, 'w') as f:
                    f.writelines(allocations_print)
                return "Allocations saved to the file '%s'" % filename
            else:
                return allocations
        except Exception as e:
            raise e

    def print_unallocated(self, filename=None):
        """

        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        try:
            staff = [' '.join((staff.first_name, staff.last_name,
                               "Staff", '\n'))
                     for staff in self.get_unallocated_staff()]
            fellows_with_neither_allocations = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow", '\n'))
                    for fellow in self.get_fellows_with_no_allocation()]
            fellows_with_only_living_space = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow", "-",
                     fellow.allocated_living_space.name, '\n'))
                     for fellow in self.get_fellows_with_living_space_only()]
            fellows_with_only_office_space = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow",
                     fellow.allocated_office_space.name, "-", '\n'))
                     for fellow in self.get_fellows_with_office_space_only()]
            fellows = fellows_with_neither_allocations \
                + fellows_with_only_living_space \
                + fellows_with_only_office_space

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
            return {"filename": filename, "unallocated": unallocated,
                    "message": message}
        except Exception as e:
            raise e

    def print_room(self, room_name):
        """

        :param room_name:
        :type room_name:
        :return:
        :rtype:
        """
        if not isinstance(room_name, str):
            raise TypeError
        rooms = self.get_all_rooms()
        room_name = room_name.lower()
        people_count = 0
        if rooms:
            if room_name in [room.name.lower() for room in rooms]:
                for staff in self.staff:
                    if isinstance(staff.allocated_office_space, Office):
                        if room_name == \
                                staff.allocated_office_space.name.lower():
                            print("%s %s %s" % (
                                staff.first_name, staff.last_name, "Staff"))
                            people_count += 1
                for fellow in self.fellows:
                    if isinstance(fellow.allocated_office_space, Office):
                        if room_name == \
                                fellow.allocated_office_space.name.lower():
                            print("%s %s %s" % (
                                fellow.first_name, fellow.last_name, "Fellow"))
                            people_count += 1
                    elif isinstance(
                            fellow.allocated_living_space, LivingSpace):
                        if room_name == \
                                fellow.allocated_living_space.name.lower():
                            print("%s %s %s" % (
                                fellow.first_name, fellow.last_name, "Fellow"))
                            people_count += 1

                if not people_count:
                    # Room is empty
                    return Config.error_codes[16] + ": '%s'" % room_name
            else:
                # Room does not exist
                return Config.error_codes[1] + ": '%s'" % room_name
        else:
            return "There are no rooms yet"

        return people_count

    def save_state(self, database_name=None, path=None, override=False):
        """

        :param path:
        :type path:
        :param database_name:
        :type database_name:
        :param override:
        :type override:
        :return:
        :rtype:
        """
        try:
            if database_name:
                if set('[~!@#$%^&*()+{}"/\\:;\']+$').intersection(
                        database_name):
                    return Config.error_codes[17] + " '%s'" % database_name
            else:
                database_name = Config.default_db_name

            if path:
                database_file_path = path + "/" + database_name
            else:
                database_file_path = Config.database_directory + database_name
            db_path = Path(database_file_path)

            if not self.offices + self.living_spaces + self.fellows \
                    + self.staff:
                return "No data to save"

            if db_path.is_file() and not override and database_name != \
                    Config.default_db_name:
                self.print_info(
                        "About to override database '%s'" % database_name)
                while True:
                    override = input(colored("Override? (Y/N): ", 'green'))
                    if override.lower() in Config.allowed_yes_strings:
                        break
                    elif override.lower() in Config.allowed_no_strings:
                        return "Aborting save state"
                    else:
                        self.print_info("Invalid Option")

            self.print_info("Database Path: %s" % database_file_path)
            connection = sqlite3.connect(database_file_path)
            if isinstance(connection, sqlite3.Connection):
                cursor = connection.cursor()
                self.print_info("Creating rooms table...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rooms
                    (name varchar(50) PRIMARY KEY,
                    type varchar(15))
                      ''')
                self.print_info("Creating people table...")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS people
                    (id INTEGER PRIMARY KEY,
                    first_name varchar(50) NOT NULL,
                    last_name varchar(50) NOT NULL,
                    role varchar(50),
                    allocated_office_space varchar(50),
                    allocated_living_space varchar(50),
                    wants_accommodation INTEGER DEFAULT 0)
                  ''')

                # Save data to database
                if self.get_all_rooms():
                    self.print_info("Saving rooms to Database...")
                    cursor.executemany(
                            "INSERT OR REPLACE INTO rooms (name, "
                            "type) values (?, ?)", self.tuplize_room_data(
                                    self.get_all_rooms()))
                if self.fellows:
                    self.print_info("Saving fellows to Database...")
                    cursor.executemany("INSERT OR REPLACE INTO people (id, "
                                       "first_name, last_name, "
                                       "role, allocated_office_space, "
                                       "allocated_living_space, "
                                       "wants_accommodation) values "
                                       "(?, ?, ?, ?, ?, ?, ?)",
                                       self.tuplize_fellow_data(self.fellows))
                if self.staff:
                    self.print_info("Saving staff to Database...")
                    cursor.executemany("INSERT OR REPLACE INTO people (id, "
                                       "first_name, last_name, role, "
                                       "allocated_office_space, "
                                       "allocated_living_space, "
                                       "wants_accommodation) "
                                       "values (?, ?, ?, ?, ?, ?, ?)",
                                       self.tuplize_staff_data(self.staff))
                connection.commit()
                connection.close()
            else:
                self.print_info("Data not saved")
                return connection
        except TypeError as error:
            raise error
        except Exception as e:
            # Print out the sqlite error
            self.print_error("Error: %s" % e)

    def load_state(self, database_name=None, path=None):
        """

        :param database_name:
        :type database_name:
        :param path:
        :type path:
        :return:
        :rtype:
        """
        try:
            if database_name:
                if set('[~!@#$%^&*()+{}"/\\:;\']+$').intersection(
                        database_name) and database_name not in \
                        Config.special_databases:
                    return Config.error_codes[17] + " '%s'" % database_name
            else:
                database_name = Config.default_db_name

            if path:
                database_file_path = path + "/" + database_name
            else:
                database_file_path = Config.database_directory + database_name
            self.print_info("Database path: '%s'" % database_file_path)

            db_path = Path(database_file_path)

            if not db_path.is_file():
                return Config.error_codes[18] + " '%s'" % database_name

            connection = sqlite3.connect(database_file_path)
            if isinstance(connection, sqlite3.Connection):
                self.print_info("Loading data from the database...")
                cursor = connection.cursor()
                # Check if database is empty
                cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' "
                        "AND name='people';")
                data = cursor.fetchall()
                cursor.execute("SELECT name FROM sqlite_master WHERE "
                               "type='table' AND name='rooms';")
                data += cursor.fetchall()
                if not data:
                    return "No data to Load. Empty database '%s'" % \
                           database_name
                cursor.execute("SELECT * FROM people")
                people = cursor.fetchall()
                cursor.execute("SELECT * FROM rooms")
                rooms = cursor.fetchall()
                room_objects = self.add_room_database_data_to_amity(rooms)
                people_objects = self.add_people_database_data_to_amity(people)

                connection.close()
                return {"people": people_objects, "rooms": room_objects}
            else:
                return connection
        except Exception as e:
            raise e

    def add_people_database_data_to_amity(self, people_list):
        """

        :param people_list:
        :type people_list:
        :return:
        :rtype:
        """
        loaded_fellows = []
        modified_fellows = []
        loaded_staff = []
        modified_staff = []
        for person in people_list:
            if person[3].lower() in Config.allowed_fellow_strings:

                if person[0] in [fellow.person_id for fellow in self.fellows]:
                    # get fellow with similar id and apply values
                    fellow = self.get_person_object_from_id(person[0])
                    fellow_before = fellow
                    fellow.first_name = person[1]
                    fellow.last_name = person[2]
                    fellow.allocated_office_space = \
                        self.get_room_object_from_name(person[4])
                    fellow.allocated_living_space = \
                        self.get_room_object_from_name(person[5])
                    fellow.wants_accommodation = True if person[6] else False
                    if fellow_before != fellow:
                        modified_fellows.append(fellow)
                    else:
                        modified_fellows = []
                elif person[0] in [staff.person_id for staff in self.staff]:
                    self.print_info("A staff member with the ID '%s' already "
                                    "exists. Not loading Fellow '%s' '%s"
                                    % (person[0], person[1], person[2]))
                else:
                    # Create a new fellow
                    fellow = Fellow(
                            person[1], person[2], person_id=person[0],
                            allocated_living_space=self.
                            get_room_object_from_name(person[5]),
                            wants_accommodation=True if person[6]
                            else False)
                    fellow.allocated_office_space = \
                        self.get_room_object_from_name(person[4])

                    # Only append new fellow
                    self.fellows.append(fellow)
                    loaded_fellows.append(fellow)
            elif person[3].lower() in Config.allowed_staff_strings:
                # should actually check for all people not just the type
                if person[0] in [staff.person_id for staff in self.staff]:
                    # get staff with similar id and apply values
                    staff = self.get_person_object_from_id(person[0])
                    staff_before = staff
                    staff.person_id = person[0]
                    staff.first_name = person[1]
                    staff.last_name = person[2]
                    staff.allocated_office_space = \
                        self.get_room_object_from_name(person[4])
                    if staff_before != staff:
                        modified_staff.append(staff)
                    else:
                        modified_staff = []
                elif person[0] in [fellow.person_id for fellow
                                   in self.fellows]:
                    self.print_info("A fellow with the ID '%s' already "
                                    "exists. Not loading Staff '%s' '%s"
                                    % (person[0], person[1], person[2]))
                else:
                    # Create an entirely new Staff object
                    staff = Staff(person[1], person[2], person_id=person[0])
                    staff.allocated_office_space = \
                        self.get_room_object_from_name(person[4])
                    # Only append new staff
                    self.staff.append(staff)
                    loaded_staff.append(staff)
            else:
                self.print_error("%s '%s'" % (Config.error_codes[5], person[
                    3]))
                self.print_error('Skipping invalid data...')
        loaded_people = {
            "loaded_fellows": loaded_fellows,
            "modified_fellows": modified_fellows,
            "loaded_staff": loaded_staff,
            "modified_staff": modified_staff}
        return loaded_people

    def add_room_database_data_to_amity(self, room_list):
        """

        :param room_list:
        :type room_list:
        :return:
        :rtype:
        """
        loaded_offices = []
        loaded_living_spaces = []
        for room in room_list:
            if room[1].lower() in Config.allowed_office_strings:
                if room[0] in [office.name for office in self.offices]:
                    self.print_info("An office with the name '%s' already "
                                    "exists. Skipping loading of duplicate "
                                    "office..."
                                    % (room[0]))
                elif room[0] in [living_space.name for living_space
                                 in self.living_spaces]:
                    self.print_info("A Living Space with the name '%s' "
                                    "already exists. Skipping loading of "
                                    "office with duplicate name..."
                                    % (room[0]))
                else:
                    # Create an entirely new Office
                    office = Office(room[0])
                    self.offices.append(office)
                    loaded_offices.append(office)
            elif room[1].lower() in Config.allowed_living_space_strings:
                if room[0] in [living_space.name for living_space
                               in self.living_spaces]:
                    self.print_info("A living space with the name '%s' "
                                    "already exists. Skipping loading of "
                                    "duplicate living space..."
                                    % (room[0]))
                elif room[0] in [office.name for office in self.offices]:
                    self.print_info("A Living Space with the name '%s' "
                                    "already exists. Skipping loading of "
                                    "office with duplicate name..."
                                    % (room[0]))
                else:
                    # Create an entirely new Living Space
                    living_space = LivingSpace(room[0])
                    self.living_spaces.append(living_space)
                    loaded_living_spaces.append(living_space)
            else:
                self.print_error("%s '%s'" % (Config.error_codes[6], room[1]))
                self.print_error('Skipping invalid data...')
        return {"loaded_offices": loaded_offices,
                "loaded_living_spaces": loaded_living_spaces}

    def get_room_object_from_name(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        if name:
            if isinstance(name, str):
                room = [room for room in self.get_all_rooms() if
                        room.name.lower() == name.lower()]
                if room:
                    return room[0]
                else:
                    return "The room %s does not exist" % name
            else:
                return "Room name must be a string"

    def get_person_object_from_id(self, person_id):
        """

        :param person_id:
        :type person_id:
        :return:
        :rtype:
        """
        if person_id:
            try:
                person_id = int(person_id)
                person = [person for person in self.get_all_people()
                          if person.person_id == person_id]
            except ValueError:
                return 'The person id must be an Integer'
            if person:
                return person[0]
        return "Person with the ID '%s' does not exist" % person_id

    def get_all_rooms(self):
        """

        :return:
        :rtype:
        """
        return self.offices + self.living_spaces

    def get_all_people(self):
        """

        :return:
        :rtype:
        """
        return self.fellows + self.staff

    def get_allocated_staff(self):
        """

        :return:
        :rtype:
        """
        return [staff for staff in self.staff if isinstance(
                staff.allocated_office_space, Office)]

    def get_fellows_allocated_both(self):
        """

        :return:
        :rtype:
        """
        return [fellow for fellow in self.fellows
                if fellow.allocated_office_space and
                fellow.allocated_living_space]

    def get_unallocated_staff(self):
        """

        :return:
        :rtype:
        """
        return [staff for staff in self.staff
                if not staff.allocated_office_space]

    def get_fellows_with_no_allocation(self):
        """

        :return:
        :rtype:
        """
        return [fellow for fellow in self.fellows
                if not fellow.allocated_living_space and not
                fellow.allocated_office_space]

    def get_fellows_with_office_space_only(self):
        """

        :return:
        :rtype:
        """
        return [fellow for fellow in self.fellows
                if fellow.allocated_office_space and not
                fellow.allocated_living_space and fellow.wants_accommodation]

    def get_fellows_with_living_space_only(self):
        """

        :return:
        :rtype:
        """
        return [fellow for fellow in self.fellows
                if fellow.allocated_living_space and not
                fellow.allocated_office_space]

    @staticmethod
    def tuplize_room_data(room_list):
        """

        :param room_list:
        :type room_list:
        :return:
        :rtype:
        """
        tuple_list = []
        for room in room_list:
            tuple_list.append((
                room.name, "office" if isinstance(room, Office)
                else "living-space"))
        return tuple_list

    @staticmethod
    def tuplize_fellow_data(fellows_list):
        """
        Convert fellow object data into a tuple for database insertion
        :param fellows_list:
        :type fellows_list:
        :return:
        :rtype:
        """
        tuple_list = []
        for fellow in fellows_list:
            if fellow.allocated_office_space:
                allocated_office_space = fellow.allocated_office_space.name
            else:
                allocated_office_space = None

            if fellow.allocated_living_space:
                allocated_living_space = fellow.allocated_living_space.name
            else:
                allocated_living_space = None
            tuple_list.append((
                fellow.person_id,
                fellow.first_name,
                fellow.last_name,
                "fellow",
                allocated_office_space,
                allocated_living_space,
                1 if fellow.wants_accommodation else 0
            ))
        return tuple_list

    @staticmethod
    def tuplize_staff_data(staff_list):
        """

        :param staff_list:
        :type staff_list:
        :return:
        :rtype:
        """
        tuple_list = []
        for staff in staff_list:
            if staff.allocated_office_space:
                allocated_office_space = staff.allocated_office_space.name
            else:
                allocated_office_space = None

            tuple_list.append((
                staff.person_id,
                staff.first_name,
                staff.last_name,
                "staff",
                allocated_office_space,
                None,
                0
            ))
        return tuple_list

    @staticmethod
    def translate_fellow_data_to_dict(fellow_list):
        """

        :param fellow_list:
        :type fellow_list:
        :return:
        :rtype:
        """
        fellow_dict_list = []
        for fellow in fellow_list:
            fellow_dict = {}
            for key, value in fellow.__dict__.items():
                if issubclass(type(value), Room):
                    value = value.name
                fellow_dict[key] = value
            fellow_dict['role'] = "fellow"
            fellow_dict_list.append(fellow_dict)
        return fellow_dict_list

    @staticmethod
    def translate_staff_data_to_dict(staff_list):
        """

        :param staff_list:
        :type staff_list:
        :return:
        :rtype:
        """
        staff_dict_list = []
        for staff in staff_list:
            staff_dict = {}
            for key, value in staff.__dict__.items():
                if issubclass(type(value), Room):

                    value = value.name
                staff_dict[key] = value
            staff_dict['role'] = "staff"
            staff_dict_list.append(staff_dict)
        return staff_dict_list

    @staticmethod
    def translate_room_data_to_dict(office_list, living_space_list):
        """

        :param office_list:
        :type office_list:
        :param living_space_list:
        :type living_space_list:
        :return:
        :rtype:
        """
        office_dict_list = [office.__dict__ for office in office_list]
        living_space_dict_list = [living_space.__dict__ for living_space
                                  in living_space_list]
        for office in office_dict_list:
            office['type'] = "office"
        for living_space in living_space_dict_list:
            living_space['type'] = "living-space"

        return office_dict_list + living_space_dict_list

    @staticmethod
    def print_info(text):
        """

        :param text:
        :type text:
        :return:
        :rtype:
        """
        cprint("\t%s" % text, 'cyan')\


    @staticmethod
    def print_info_result(text):
        """

        :param text:
        :type text:
        :return:
        :rtype:
        """
        cprint("\t| %s\n" % text, 'blue')

    @staticmethod
    def print_error(text):
        """

        :param text:
        :type text:
        :return:
        :rtype:
        """
        cprint("\t%s" % text, 'magenta')\



# camelot = Office("Camelot")
# ant = LivingSpace("Ant")
# jane = Fellow("Jane", "Kay", person_id=2, allocated_office_space="camelot",
#               allocated_living_space="ant")
# #
# a = Amity()
# a.get_person_object_from_id(jane.person_id)
# a.offices = [camelot]
# jane.allocated_office_space = camelot
#
# a.add_person("Kate", "Mitch", "staff")
# a.add_person("Maria", "Mitch", "staff")
# a.fellows += [jane]
#
# a.load_people('files/test_people.in')

# a.save_state()
#
# people = a.get_all_people()
# for person in people:
#     print("Person: ", person.__dict__)
#
# print("\nJane: ", jane.__dict__)
# print("\nKate: ", a.staff[0].__dict__)
# print("\nMaria: ", str(a.staff[1].__dict__))
# print("\nMaria: ", str(a.offices[0].__dict__))
