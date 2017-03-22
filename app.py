#!/usr/bin/env python
# coding=utf-8

"""
Amity.
A room allocation system for Fellows and Staff.

Usage:
    app.py create_room <room_name>... [-l|-o]
    app.py add_person <first_name> <last_name> <role> [<wants_accommodation>]
    app.py reallocate_person <person_identifier> <new_room_name>
    app.py load_people <filename>
    app.py print_allocations [-o=filename]
    app.py print_unallocated [-o=filename]
    app.py print_room <room_name>
    app.py save_state [--db=sqlite_database]
    app.py load_state [<sqlite_database>]
    app.py list_people
    app.py list_fellows
    app.py list_staff
    app.py list_rooms
    app.py list_offices
    app.py list_living_spaces
    app.py (-h | --help)
    app.py (-v | --version)
    app.py (-i | --interactive)
    app.py quit
    quit

Arguments
    <room_name>           The name of the room to be created or printed.
                          Add '-ls' at the end of the room name to
                          indicate that it is a living space. Default is office
    <first_name>          The first name of the Fellow or Staff
    <last_name>           The last name of the Fellow or Staff
    <role>                The role of the new person, either Fellow or Staff
    <wants_accommodation> Indication of if the Fellow wants accommodation or
                          not. Choices ('N','No', 'Yes','Y')
    <person_identifier>   A Unique User identifier of the Fellow or Staff
    <new_room_name>       The Room name to which the Fellow or Staff is to be
                          reallocated
    <filename>            The file to load from or save data to
    <sqlite_database>     The database to load from or save data to

Options:
    -i --interactive        Interactive Mode
    -h --help               Show this screen and exit from amity
    --o FILENAME            Specify filename
    --db sqlite_database     Name of SQLite Database to load from or save
    data to
    -v --version
"""

import os
import cmd
import sys
from pyfiglet import figlet_format
from termcolor import cprint, colored
from docopt import docopt, DocoptExit
from terminaltables import AsciiTable

from models.amity import Amity
from models.room import Office, LivingSpace
from models.person import Staff, Fellow


def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action
    """
    def fn(self, args):
        """

        :param self:
        :type self:
        :param args:
        :type args:
        :return:
        :rtype:
        """
        try:
            opt = docopt(fn.__doc__, args)
        except DocoptExit as error:
            # The DocoptExit is thrown when the arguments do not match
            print('Invalid Command Entered!')
            print(error)
            return
        except SystemExit:
            # The SystemExit exception prints the usage for --help
            return
        return func(self, opt)

    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)
    return fn


def print_header():
    """
        Create a header to be displayed when the program starts
    """
    os.system("clear")
    print("\n")
    cprint(figlet_format('AMITY', font='colossal'), 'blue')
    cprint('-' * 52, 'blue')
    cprint("%sA ROOM ALLOCATION SYSTEM." % (" " * 14), 'cyan')


def pretty_print_data(list_of_dicts):
    """

    :param list_of_dicts:
    :type list_of_dicts:
    """

    if list_of_dicts:
        key_list = [key for key in list_of_dicts[0].keys()]
        formatted_key_list = [
            colored(key.title().split('__')[-1], 'green') for key in
            list_of_dicts[0].keys()]
        table_rows = [formatted_key_list]

        for obj in list_of_dicts:
            # Initialize row data with Null values to enable indexing
            row_data = [None] * len(key_list)
            for key, value in obj.items():
                row_data[key_list.index(key)] = (colored(value, 'blue'))
            table_rows.append(row_data)
    else:
        table_rows = [["No data to Print"]]
    table = AsciiTable(table_rows)
    cprint(table.table, 'green')


def print_subtitle(text):
    """

    :param text:
    :type text:
    """
    cprint("\n\n%s\n%s" % (text, "-" * len(text)), 'cyan')


def print_info(text):
    """

    :param text:
    :type text:
    """
    cprint("\n%s" % text, 'blue')


def print_error(text):
    """

    :param text:
    :type text:
    """
    cprint("\n%s\n%s\n%s" % ("-"*len(text), text, "-"*len(text)), 'magenta')


class AmityInteractive(cmd.Cmd):
    """
        The Amity Command Line Interface to be used for User interaction
    """
    intro = colored("\nWelcome to my Amity!"
                    + "\n\t<Type 'help' to see the list of available "
                      "commands>\n", 'blue', attrs=['dark'])

    amity_prompt = colored('Amity # ', 'blue', attrs=['bold'])
    prompt = amity_prompt

    @docopt_cmd
    def do_create_room(self, args):
        """
        Create one or more rooms in Amity

        Info:   Add '-ls' at the end of the room name to indicate that it
                is a living space.
                Offices are created by default (i.e. if there is no '-l'
                option)
        Usage: create_room <room_name>... [-l|-o]
        """
        rooms = args['<room_name>']

        if args['-l']:
            new_rooms = amity.create_room(rooms, 'living-space')
        else:
            # Default room setting is office
            new_rooms = amity.create_room(rooms)

        if isinstance(new_rooms, str):
            print_error(new_rooms)
        offices = [office for office in new_rooms if isinstance(
                office, Office)]
        living_spaces = [living_space for living_space in new_rooms if
                         isinstance(living_space, LivingSpace)]
        room_data = amity.translate_room_data_to_dict(offices, living_spaces)
        print_subtitle("Newly Created Rooms")
        pretty_print_data(room_data)

    @docopt_cmd
    def do_add_person(self, args):
        """
        Adds a person to the system and allocates the person to a random room.

        Arguments:
            <first_name> User's first name
            <last_name> User's last name
            <role> specifies the role of the person being added
            ('Fellow' or 'Staff')
            [<wants_accommodation>] Indicates if user wants accommodation or
            not. It only accepts 'Y','Yes','No'or 'N'

        Usage:
            add_person <first_name> <last_name> <role> [<wants_accommodation>]
        """
        first_name = args['<first_name>']
        last_name = args['<last_name>']
        role = args['<role>']
        if role.lower() not in amity.allowed_fellow_strings + \
                amity.allowed_staff_strings:
            print_info("Invalid arguments. \n- <role>  can either be "
                       "'Fellow' or 'Staff' ")
            return
        wants_accommodation = args['<wants_accommodation>'] or 'N'
        if wants_accommodation.lower() not in amity.allowed_yes_strings + \
                amity.allowed_no_strings:
            print_info("Invalid  arguments. \n- <wants_accommodation> can "
                       "either be among %s" % (
                        amity.allowed_yes_strings + amity.allowed_no_strings
                        ))
            return
        wants_accommodation = True if wants_accommodation in \
            amity.allowed_yes_strings else False

        new_person = amity.add_person(first_name, last_name, role,
                                      wants_accommodation)
        if not isinstance(new_person, str):
            if isinstance(new_person, str):
                print_error(new_person)

            if isinstance(new_person, Staff):
                person_data = amity.translate_staff_data_to_dict([new_person])
            else:
                person_data = amity.translate_fellow_data_to_dict([new_person])

            print_subtitle("Newly Added Person")
            pretty_print_data(person_data)
        else:
            print(new_person)

    @docopt_cmd
    def do_reallocate_person(self, args):
        """
        Reallocate the person with  person_identifier  to  <new_room_name>
        Usage: reallocate_person <person_identifier> <new_room_name>
        """
        person_id = args['<person_identifier>']
        new_room_name = args['<new_room_name>']
        person = amity.get_person_object_from_id(person_id)
        room = amity.get_room_object_from_name(new_room_name)
        if not person:
            print_info("Person with the ID '%s' does not exist" % person_id)
        if not room:
            print_info("A room with the name '%s' does not exist" %
                       new_room_name)
        if person and room:
            reallocation = amity.allocate_room_to_person(
                    person, new_room_name, True)
            if not isinstance(reallocation, str):
                if isinstance(person, Staff):
                    person_data = amity.translate_staff_data_to_dict([person])
                else:
                    person_data = amity.translate_fellow_data_to_dict([person])

                print_subtitle("Reallocated Person")
                pretty_print_data(person_data)
            else:
                print_error(reallocation)

    @docopt_cmd
    def do_load_people(self, args):
        """
        Adds people to rooms from a txt file.
        Usage: load_people <filename>
        """
        loaded_people = amity.load_people(args['<filename>'])
        if isinstance(loaded_people, str):
            print_error(loaded_people)
        else:
            fellows = [fellow for fellow in loaded_people if isinstance(
                    fellow, Fellow)]
            staff = [staff for staff in loaded_people if isinstance(
                    staff, Staff)]
            fellow_data = amity.translate_fellow_data_to_dict(fellows)

            staff_data = amity.translate_staff_data_to_dict(staff)

            print_subtitle("Newly Created People from File")
            pretty_print_data(staff_data + fellow_data)

    @docopt_cmd
    def do_print_allocations(self, args):
        """
        Prints a list of allocations onto the screen
        Usage: print_allocations [--o=FILENAME]
        """
        allocations = amity.print_allocations(args['--o'])
        if isinstance(allocations, str):
            print_error(allocations)
        else:
            fellows = [fellow for fellow in allocations if isinstance(
                    fellow, Fellow)]
            staff = [staff for staff in allocations if isinstance(
                    staff, Staff)]
            fellow_data = amity.translate_fellow_data_to_dict(fellows)

            staff_data = amity.translate_staff_data_to_dict(staff)

            print_subtitle("Amity Allocations")
            pretty_print_data(staff_data + fellow_data)

    @docopt_cmd
    def do_print_unallocated(self, args):
        """
        Prints a list of allocations onto the screen.
        Usage: print_unallocated [--o=FILENAME]
        """
        result = amity.print_unallocated(args['--o'])
        if isinstance(result, str):
            print_info(result)

    @docopt_cmd
    def do_print_room(self, args):
        """
        Prints the names of all the people in  room_name  on the
        screen.
        Usage: print_room <room_name>
        """
        result = amity.print_room(args['<room_name>'])
        if isinstance(result, str):
            print_info(result)

    @docopt_cmd
    def do_save_state(self, args):
        """
        Persists all the data stored in the app to a SQLite database
        Usage: save_state [--db=sqlite_database]
        """
        if args['--db']:
            result = amity.save_state(args['--db'])
        else:
            result = amity.save_state()

        if isinstance(result, str):
            print_info(result)

    @docopt_cmd
    def do_load_state(self, args):
        """
        Loads data from a database into the application.
        Usage: load_state [<sqlite_database>]
        """
        if args['<sqlite_database>']:
            path = args['<sqlite_database>'].split('/')[:-1]
            database_name = args['<sqlite_database>'].split('/')[-1]
            result = amity.load_state(database_name, path)
        else:
            result = amity.load_state()

        if isinstance(result, str):
            print_info(result)\


    @staticmethod
    def do_quit(args):
        """ Quits Amity
        :param args:
        :type args:
        """
        print("Ciao!")
        exit()

    # @docopt_cmd
    # def do_list_people(self):
    #     """
    #     List everyone in amity.
    #     """
    #     if args['<sqlite_database>']:
    #         path = args['<sqlite_database>'].split('/')[:-1]
    #         database_name = args['<sqlite_database>'].split('/')[-1]
    #         result = amity.load_state(database_name, path)
    #     else:
    #         result = amity.load_state()
    #
    #     if isinstance(result, str):
    #         print_info(result)
    #
    # app.py
    # list_people
    # app.py
    # list_fellows
    # app.py
    # list_staff
    # app.py
    # list_rooms
    # app.py
    # list_offices
    # app.py
    # list_living_spaces


opt = docopt(__doc__, sys.argv[1:])

if opt['--interactive']:
    print_header()
    amity = Amity()
    AmityInteractive().cmdloop()
