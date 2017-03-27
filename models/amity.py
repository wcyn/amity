import re
import sqlite3
import random

from pathlib import Path

from termcolor import cprint, colored

from models.config import Config
from models.database import Database
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
            self.randomly_allocate_room(
                    new_person, Config.allowed_office_strings[0])

            if wants_accommodation:
                if role.lower() in Config.allowed_fellow_strings:
                    # Randomly assign available living space to fellow
                    self.randomly_allocate_room(
                            new_person, Config.allowed_living_space_strings[0])
                else:
                    self.print_error("%s '%s %s'" % (
                        Config.error_codes[10], new_person.first_name,
                        new_person.last_name))
            return new_person

        except TypeError as error:
            raise error
        except Exception as error:
            self.print_info(error)
            raise error

    def allocate_room_to_person(self, person, room, override=False):
        """

        :param override:
        :type override:
        :param person:
        :type person:
        :param room:
        :type room:
        :return:
        :rtype:
        """
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

                if not override:
                    reallocate = True
                    if already_allocated_office:
                        if person.allocated_office_space == room:
                            self.print_error(
                                    "'%s %s' already allocated office '%s'" %
                                    (person.first_name, person.last_name,
                                     room.name))
                            return False
                        # Person already has office space
                        self.print_info("About to move %s from %s to %s" % (
                            person.first_name,
                            person.allocated_office_space.name, room.name))
                        reallocate = self.handle_yes_no_input(
                                "Move? (Y/N): ", "Aborting Reallocation")
                    elif already_allocated_living_space:
                        if person.allocated_living_space == room:
                            self.print_error("Person already allocated "
                                             "living space '%s'" % room.name)
                            return
                        # Person already has office space
                        self.print_info("About to move %s from %s to %s" % (
                            person.first_name,
                            person.allocated_living_space.name, room.name))
                        reallocate = self.handle_yes_no_input(
                                "Move? (Y/N): ", "Aborted Reallocation")
                    if not reallocate:
                        return  # Abort Mission

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

        room = None
        if room_type in Config.allowed_office_strings:
            if not self.offices:
                self.print_info(
                        "There exists no offices to assign to '%s %s'" % (
                            person.first_name, person.last_name))
                return None
            if offices_not_full:
                self.print_info("Randomly allocating office to %s..." %
                                person.first_name)
                # Randomly select an non full office
                office = random.choice(offices_not_full)
                self.allocate_room_to_person(person, office)
                room = office
                self.print_info_result("Allocated office: %s" % room.name)
            else:
                self.print_info("All offices are full. No office to "
                                "assign to '%s %s'" %
                                (person.first_name, person.last_name))
        else:
            if not self.living_spaces:
                self.print_info(
                        "There exists no living spaces to assign to fellow "
                        "'%s %s'" % (person.first_name, person.last_name))
                return None
            if living_spaces_not_full:
                self.print_info("Randomly allocating living space to %s..." %
                                person.first_name)
                # Randomly select a non full living space
                living_space = random.choice(living_spaces_not_full)
                self.allocate_room_to_person(person, living_space)
                room = living_space
                self.print_info_result("Allocated living space: %s" % 
                                       room.name)
                # Reset wants accommodation to False since they now
                # have accommodation
                person.wants_accommodation = False
            else:
                self.print_info("No free living space to allocate '%s' to"
                                % person.first_name)
        return room

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
                    wants_accommodation = False
                    if len(person_data) == 4:
                        if person_data[3] in Config.allowed_yes_strings:
                            wants_accommodation = True

                    if person_data[2].lower() in Config.allowed_fellow_strings:
                        fellow = self.add_person(
                                person_data[0], person_data[1],
                                Config.allowed_fellow_strings[0],
                                wants_accommodation)
                        loaded_people.append(fellow)
                    elif person_data[2].lower() in \
                            Config.allowed_staff_strings:
                        staff = self.add_person(
                                person_data[0],
                                person_data[1],
                                Config.allowed_staff_strings[0],
                                wants_accommodation)
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

    def print_allocated_people(self, filename=None, path=None):
        """

        :param path:
        :type path:
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
                filename = ''.join(x for x in filename if x not in
                                   "\"'\/:*?<>|")
                if path:
                    file_path = path + "/" + filename
                else:
                    file_path = filename
                self.print_info("Printing allocations to file '%s'..."
                                % file_path)
                with open(file_path, 'w') as f:
                    f.writelines(allocations_print)
                return "Allocations saved to the file '%s'" % filename
            else:
                return allocations
        except Exception as e:
            raise e

    def print_unallocated(self, filename=None, path=None):
        """

        :param path:
        :type path:
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
                    (fellow.first_name, fellow.last_name, "Fellow",
                     "(No Office)", fellow.allocated_living_space.name, '\n'))
                     for fellow in self.get_fellows_with_living_space_only()]
            fellows_with_only_office_space = [' '.join(
                    (fellow.first_name, fellow.last_name, "Fellow",
                     fellow.allocated_office_space.name, "(No Living Space)",
                     '\n'))
                     for fellow in self.get_fellows_with_office_space_only()]
            fellows = fellows_with_neither_allocations \
                + fellows_with_only_living_space \
                + fellows_with_only_office_space

            unallocated = staff + fellows
            if not unallocated:
                return "No unallocated people data to print"

            if filename:
                if not isinstance(filename, str):
                    raise TypeError
                # Clean filename. Remove unwanted filename characters
                filename = ''.join(x for x in filename if x not in
                                   "\"'\/:*?<>|")
                if path:
                    file_path = path + "/" + filename
                else:
                    file_path = filename
                self.print_info("Printing unallocated data to file '%s'..."
                                % file_path)
                with open(file_path, 'w') as f:
                    f.writelines(unallocated)
                self.print_info("Printed to file successfully!")
            else:
                for allocation in unallocated:
                    print(allocation.strip())
            return {'filename': filename, 'unallocated': unallocated}
        except TypeError as error:
            raise error
        except FileNotFoundError as error:
            self.print_error("%s" % error)

    def print_room(self, room_name, verbose=True):
        """

        :param verbose:
        :type verbose:
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
            people = self.get_people_allocated_room(room_name)
            if isinstance(people, str):
                return people
            if not people:
                # Room is empty
                return Config.error_codes[16] + ": '%s'" % room_name
            if verbose:
                for person in people:
                    if isinstance(person, Staff):
                        print("%s %s %s" % (
                            person.first_name, person.last_name,
                            "Staff"))
                    else:
                        print("%s %s %s" % (
                            person.first_name, person.last_name,
                            "Fellow"))
            return people
        else:
            return "There are no rooms yet"

    def get_people_allocated_room(self, room_name):
        """
        Return a list of the people allocated the specified room name
        :param room_name:
        :type room_name:
        :return:
        :rtype:
        """
        room = self.get_room_object_from_name(room_name)
        if isinstance(room, Office):
            return [person for person in self.get_all_people() if
                    person.allocated_office_space == room]
        elif isinstance(room, LivingSpace):
            return [fellow for fellow in self.fellows if
                    fellow.allocated_living_space == room]
        else:
            return room

    def print_allocations(self, filename=None, path=None):
        """
        Prints rooms and the people allocated to those rooms
        """
        try:
            if not filename:
                rooms = self.get_all_rooms()
                if rooms:
                    for room in rooms:
                        self.print_subtitle(room.name)
                        people = self.print_room(room.name)
                        if isinstance(people, str):
                            cprint(people, 'yellow')
                else:
                    return "There are no rooms yet"
            else:
                if not isinstance(filename, str):
                    raise TypeError
                if path:
                    file_path = path + "/" + filename
                else:
                    file_path = filename
                # Clean filename. Remove unwanted filename characters
                filename = ''.join(x for x in filename if x not in "\/:*?<>|")
                self.print_info("Printing Allocations to file '%s'..."
                                % filename)
                # Empty the file first
                open(file_path, 'w').close()
                for room in self.get_all_rooms():
                    people = self.print_room(room.name, False)
                    if not isinstance(people, str):
                        with open(file_path, 'a') as f:
                            f.write("%s\n%s\n" % (room.name, '-' * len(
                                    room.name)))
                            for person in people:
                                if isinstance(person, Staff):
                                    f.write("%s %s %s\n" % (
                                        person.first_name,
                                        person.last_name,
                                        "Staff"))
                                else:
                                    f.write("%s %s %s\n" % (
                                        person.first_name,
                                        person.last_name,
                                        "Fellow"))
                            f.write("\n")
                    else:
                        self.print_info(people)
                self.print_info("Printed to file successfully!")
        except FileNotFoundError as error:
            self.print_error("%s" % error)

    def save_state(self, database_name=None, path=None, override=False):
        """
        Saves data from amity into a specified database file
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
                override = self.handle_yes_no_input(
                        "Override? (Y/N): ", "Aborted save state")
                if not override:
                    return

            self.print_info("Database Path: %s" % database_file_path)
            connection = sqlite3.connect(database_file_path)
            if isinstance(connection, sqlite3.Connection):
                cursor = connection.cursor()
                self.print_info("Creating rooms table...")
                Database.create_rooms_table(cursor)
                self.print_info("Creating people table...")

                # Save data to database
                if self.get_all_rooms():
                    self.print_info("Saving rooms to Database...")
                    Database.insert_room_data(
                            cursor,
                            self.tuplize_room_data(self.get_all_rooms()))
                if self.fellows:
                    self.print_info("Saving fellows to Database...")
                    Database.insert_people_data(
                            cursor, self.tuplize_fellow_data(self.fellows))
                if self.staff:
                    self.print_info("Saving staff to Database...")
                    Database.insert_people_data(
                            cursor, self.tuplize_staff_data(self.staff))
                connection.commit()
                connection.close()
                self.print_info("Data Saved Successfully")
            else:
                self.print_info("Data not saved")
                return connection
        except TypeError as error:
            raise error
        except FileNotFoundError as error:
            self.print_error("%s" % error)
        except sqlite3.OperationalError as error:
            # Print out the sqlite error
            self.print_error("%s" % error)

    def load_state(self, database_name=None, path=None):
        """
        Loads Data from an SQLITE Database into Amity
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

                if Database.database_is_empty(cursor):
                    return "No data to Load. Empty database '%s'" % \
                           database_name
                people = Database.get_all_people(cursor)
                rooms = Database.get_all_rooms(cursor)
                room_objects = self.add_room_database_data_to_amity(rooms)
                people_objects = self.add_people_database_data_to_amity(people)

                connection.close()
                return {"people": people_objects, "rooms": room_objects}
            else:
                return connection
        except FileNotFoundError as error:
            self.print_error("%s" % error)
        except sqlite3.OperationalError as error:
            self.print_error("%s" % error)

    def add_people_database_data_to_amity(self, people_list):
        """

        :param people_list:
        :type people_list:
        :return:
        :rtype:
        """
        loaded_staff = []
        modified_staff = []
        loaded_fellows = []
        modified_fellows = []
        for person_tuple in people_list:
            if person_tuple[3].lower() in Config.allowed_fellow_strings:
                fellow = self.add_fellow_database_data_to_amity(person_tuple)
                if fellow['loaded_fellow']:
                    loaded_fellows.append(fellow['loaded_fellow'])
                elif fellow['modified_fellow']:
                    modified_fellows.append(fellow['modified_fellow'])

            elif person_tuple[3].lower() in Config.allowed_staff_strings:
                staff = self.add_staff_database_data_to_amity(person_tuple)
                if staff['loaded_staff']:
                    loaded_staff.append(staff['loaded_staff'])
                elif staff['modified_staff']:
                    modified_staff.append(staff['modified_staff'])

            else:
                self.print_error("%s '%s'" % (Config.error_codes[5],
                                              person_tuple[3]))
                self.print_error('Skipping invalid data...')
        return {
            "loaded_staff": loaded_staff,
            "modified_staff": modified_staff,
            "loaded_fellows": loaded_fellows,
            "modified_fellows": modified_fellows
        }

    def add_fellow_database_data_to_amity(self, fellow_tuple):
        """
        Add Fellow Data to Amity from an SQLITE Database tuple
        :param fellow_tuple: A fellow in Amity
        :type fellow_tuple: Tuple containing fellow data
        """
        loaded_fellow = None
        modified_fellow = None
        if fellow_tuple[0] in [fellow.person_id for fellow in self.fellows]:
            # get fellow with similar id and apply values
            fellow = self.get_person_object_from_id(fellow_tuple[0])
            fellow_before = fellow
            fellow.first_name = fellow_tuple[1]
            fellow.last_name = fellow_tuple[2]
            fellow.allocated_office_space = \
                self.get_room_object_from_name(fellow_tuple[4])
            fellow.allocated_living_space = \
                self.get_room_object_from_name(fellow_tuple[5])
            fellow.wants_accommodation = True if fellow_tuple[6] else False
            if fellow_before != fellow:
                modified_fellows = fellow
        elif fellow_tuple[0] in [staff.person_id for staff in self.staff]:
            self.print_info("A staff member with the ID '%s' already "
                            "exists. Not loading Fellow '%s' '%s"
                            % (fellow_tuple[0], fellow_tuple[1],
                               fellow_tuple[2]))
        else:
            # Create a new fellow
            fellow = Fellow(
                    fellow_tuple[1], fellow_tuple[2],
                    person_id=fellow_tuple[0],
                    allocated_living_space=self.
                    get_room_object_from_name(fellow_tuple[5]),
                    wants_accommodation=True if fellow_tuple[6]
                    else False)
            fellow.allocated_office_space = \
                self.get_room_object_from_name(fellow_tuple[4])

            # Only append new fellow
            self.fellows.append(fellow)
            loaded_fellow = fellow
        return {
            "loaded_fellow": loaded_fellow,
            "modified_fellow": modified_fellow
        }

    def add_staff_database_data_to_amity(self, staff_tuple):
        """
        Add Staff data to amity from an SQLITE Database tuple
        :param staff_tuple: A staff in Amity
        :type staff_tuple: A tuple containing staff data
        """
        loaded_staff = None
        modified_staff = None
        if staff_tuple[0] in [staff.person_id for staff in self.staff]:
            # get staff with similar id and apply values
            staff = self.get_person_object_from_id(staff_tuple[0])
            staff_before = staff
            staff.person_id = staff_tuple[0]
            staff.first_name = staff_tuple[1]
            staff.last_name = staff_tuple[2]
            staff.allocated_office_space = \
                self.get_room_object_from_name(staff_tuple[4])
            if staff_before != staff:
                modified_staff = staff
            else:
                modified_staff = []
        elif staff_tuple[0] in [fellow.person_id for fellow in self.fellows]:
            self.print_info("A fellow with the ID '%s' already "
                            "exists. Not loading Staff '%s' '%s"
                            % (staff_tuple[0], staff_tuple[1], staff_tuple[2]))
        else:
            # Create an entirely new Staff object
            staff = Staff(staff_tuple[1], staff_tuple[2],
                          person_id=staff_tuple[0])
            staff.allocated_office_space = \
                self.get_room_object_from_name(staff_tuple[4])
            # Only append new staff
            self.staff.append(staff)
            loaded_staff = staff
        return {
            "loaded_staff": loaded_staff,
            "modified_staff": modified_staff
        }

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

    def randomly_allocate_unallocated(self):
        """
        Randomly Allocates Rooms to staff and fellows
        """
        staff_need_office = self.get_unallocated_staff()
        fellows_need_office = self.get_fellows_with_no_allocation() \
            + self.get_fellows_with_living_space_only()
        need_living_space = self.get_fellows_requiring_accommodation()
        allocated_staff = []
        allocated_fellows = []
        for staff in staff_need_office:
            room = self.randomly_allocate_room(
                    staff, Config.allowed_office_strings[0])
            if issubclass(type(room), Room):
                allocated_staff.append(staff)
        for fellow in fellows_need_office:
            room = self.randomly_allocate_room(
                    fellow, Config.allowed_office_strings[0])
            if issubclass(type(room), Room):
                allocated_fellows.append(fellow)
        for fellow in need_living_space:
            room = self.randomly_allocate_room(
                fellow, Config.allowed_living_space_strings[0]
            )
            if issubclass(type(room), Room):
                allocated_fellows.append(fellow)
        return {'staff': allocated_staff,
                'fellows': allocated_fellows}

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
                    return "%s: '%s'" % (Config.error_codes[1], name)
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
                return 'The person id must be an integer'
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

    def get_fellows_requiring_accommodation(self):
        """

        :return:
        :rtype:
        """
        return [fellow for fellow in self.fellows
                if not fellow.allocated_living_space and
                fellow.wants_accommodation]

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
        cprint("\t%s" % text, 'cyan')

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
    def print_subtitle(text):
        """

        :param text:
        :type text:
        """
        cprint("\n %s \n %s " % (" " * len(text), text), 'blue', attrs=[
            'reverse', 'bold'])

    @staticmethod
    def print_error(text):
        """

        :param text:
        :type text:
        :return:
        :rtype:
        """
        cprint("\t%s" % text, 'magenta')

    def handle_yes_no_input(self, prompt, no_clause):
        """

        :return:
        :rtype:
        """
        while True:
            override = input(
                    colored(prompt, 'green'))
            if override.lower() in Config.allowed_yes_strings:
                return True
            elif override.lower() in Config.allowed_no_strings:
                self.print_error(no_clause)
                return False
            else:
                self.print_info("Invalid Option")
