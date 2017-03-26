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
    app.py list_people [-f|-s]
    app.py list_rooms [-o|-l]
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
from models.config import Config
from models.person import Staff, Fellow
from models.room import Office, LivingSpace


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
            option = docopt(fn.__doc__, args)
        except DocoptExit as error:
            # The DocoptExit is thrown when the arguments do not match
            print_error('Invalid Command Entered!')
            fn_name = '_'.join(fn.__name__.split('_')[1:])
            print_info('Type `help %s` to view the documentation for the `%s` '
                       'command' % (fn_name, fn_name))
            print_subtitle('Here is the usage for `%s`' % fn_name)
            print_info(fn.__doc__.split('Usage:')[-1].strip())
            print_error(error)
            return
        except SystemExit:
            # The SystemExit exception prints the usage for --help
            return
        return func(self, option)

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

    cprint(figlet_format('AMITY', font='colossal'), 'blue', attrs=[
        'bold'])
    cprint('-' * 55, 'blue')
    cprint("%sA ROOM ALLOCATION SYSTEM." % (" " * 14), 'cyan')


def format_dict_keys(keys):
    """
    Generate a more readable string from the Dictionary Key
    :param keys:
    :type keys:
    :return:
    :rtype:
    """
    formatted = []
    for key in keys:
        formatted.append(' '.join(key.title().split('__')[-1].split('_')))
    return formatted


def color_list(items, color, attrs=[]):
    """
    Color the list of strings with the specified color
    :param attrs:
    :type attrs:
    :param items:
    :type items:
    :param color:
    :type color:
    :return: Returns the list of strings with the specified color
    :rtype:
    """
    return [colored(item, color, attrs=attrs) for item in items]


def print_loaded_people(people_dict):
    """

    :param people_dict:
    :type people_dict:
    """
    if people_dict['loaded_fellows'] \
            or people_dict['loaded_staff']:
        people = amity.translate_fellow_data_to_dict(
                people_dict['loaded_fellows']) + \
                 amity.translate_staff_data_to_dict(
                         people_dict['loaded_staff'])
        print_subtitle("Loaded People")
        pretty_print_data(people)
    else:
        print_info("No new people were loaded from the database")

    if people_dict['modified_fellows'] \
            or people_dict['modified_staff']:
        modified_people = amity.translate_fellow_data_to_dict(
                people_dict['modified_fellows']) + \
                          amity.translate_staff_data_to_dict(
                                  people_dict['modified_staff'])
        print_subtitle("Modified People")
        pretty_print_data(modified_people)


def print_loaded_rooms(rooms_dict):
    """

    :param rooms_dict:
    :type rooms_dict:
    """
    if rooms_dict['loaded_offices'] or rooms_dict['loaded_living_spaces']:
        rooms = amity.translate_room_data_to_dict(
                rooms_dict['loaded_offices'],
                rooms_dict['loaded_living_spaces'])
        print_subtitle("Loaded Rooms")
        pretty_print_data(rooms)
    else:
        print_info("No new rooms were loaded from the database")


def pretty_print_data(list_of_dicts):
    """

    :param list_of_dicts:
    :type list_of_dicts:
    """
    if list_of_dicts:
        max_len = max([len(d) for d in list_of_dicts])
        headers = []
        table_rows = []
        not_applicable = colored('N/A', 'magenta')
        for dict_item in list_of_dicts:
            for key in dict_item.keys():
                if key not in headers:
                    headers.append(key)
            table_rows.append(color_list([dict_item[key] if key in dict_item
                              else not_applicable for key in headers]
                              + ((max_len - len(headers)) * [not_applicable]),
                            'blue'))
        table_rows.insert(0,  color_list(format_dict_keys(headers), 'blue',
                                         attrs=['dark']))

    else:
        table_rows = [[colored("No data to print", 'magenta')]]
    table = AsciiTable(table_rows)
    cprint(table.table, 'white')


def print_subtitle(text):
    """

    :param text:
    :type text:
    """
    cprint(" %s \n %s \n" % (" " * len(text), text), 'blue', attrs=[
        'reverse', 'bold'])


def print_info(text):
    """

    :param text:
    :type text:
    """
    cprint("%s" % text, 'yellow')


def print_error(text):
    """

    :param text:
    :type text:
    """
    if isinstance(text, str):
        cprint("\n%s\n%s\n%s" % ("-" * len(text), text,
                                 "-" * len(text)), 'magenta')


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
        Usage:
            create_room <room_name>... [-l|-o]
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
            <role> The role of the person being added ('Fellow' or 'Staff')
            [<wants_accommodation>] Indicates if user wants accommodation or
            not. It only accepts 'Y','Yes','No'or 'N'

        Usage:
            add_person <first_name> <last_name> <role> [<wants_accommodation>]
        """
        first_name = args['<first_name>']
        last_name = args['<last_name>']
        role = args['<role>']
        if role.lower() not in Config.allowed_fellow_strings + \
                Config.allowed_staff_strings:
            print_info("Invalid arguments. \n- <role>  can either be "
                       "'Fellow' or 'Staff' ")
            return
        wants_accommodation = args['<wants_accommodation>'] or 'N'
        if wants_accommodation.lower() not in Config.allowed_yes_strings + \
                Config.allowed_no_strings:
            print_info("Invalid  arguments. \n- <wants_accommodation> can "
                       "either be among %s" % (
                           Config.allowed_yes_strings +
                           Config.allowed_no_strings
                       ))
            return
        wants_accommodation = True if wants_accommodation in \
            Config.allowed_yes_strings else False

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
        if isinstance(person, str):
            print_info(person)
        elif isinstance(room, str):
            print_info(room)
        elif person and room:
            reallocation = amity.allocate_room_to_person(
                person, room, True)
            if not isinstance(reallocation, str):
                if isinstance(person, Staff):
                    person_data = amity.translate_staff_data_to_dict([person])
                else:
                    person_data = amity.translate_fellow_data_to_dict([person])
                print_subtitle("Reallocated Person")
                pretty_print_data(person_data)
            else:
                print_error(reallocation)
        else:
            print_info('Arguments not provided')

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
            path = ' '.join(args['--db'].split('/')[:-1])
            database_name = args['--db'].split('/')[-1]
            result = amity.save_state(database_name, path)
        else:
            result = amity.save_state(None, 'databases')

        if isinstance(result, str):
            print_info(result)

    @docopt_cmd
    def do_load_state(self, args):
        """
        Loads data from a database into the application.
        Usage: load_state [<sqlite_database>]
        """
        if args['<sqlite_database>']:
            path = ' '.join(args['<sqlite_database>'].split('/')[:-1])
            database_name = args['<sqlite_database>'].split('/')[-1]
            result = amity.load_state(database_name, path)
        else:
            result = amity.load_state(None, 'databases')

        if isinstance(result, str):
            print_info(result)
        else:
            print_loaded_people(result['people'])
            print_loaded_rooms(result['rooms'])

    @staticmethod
    def do_quit(args):
        """ Quits Amity
        :param args:
        :type args:
        """
        print("\nCiao!")
        exit()

    @docopt_cmd
    def do_list_people(self, args):
        """
        List the people in amity.
        Usage: list_people [-f|-s]
        """
        if args['-f']:
            people = amity.translate_fellow_data_to_dict(amity.fellows)
        elif args['-s']:
            people = amity.translate_staff_data_to_dict(amity.staff)
        else:
            fellows = amity.translate_fellow_data_to_dict(amity.fellows)
            staff = amity.translate_staff_data_to_dict(amity.staff)
            people = fellows + staff

        if isinstance(people, str):
            print_info(people)
        else:
            pretty_print_data(people)\


    @docopt_cmd
    def do_list_rooms(self, args):
        """
        List rooms in amity.
        Usage: list_rooms [-o|-l]
        """
        offices = amity.translate_room_data_to_dict(amity.offices, [])
        living_spaces = amity.translate_room_data_to_dict(
                [], amity.living_spaces)
        if args['-o']:
            rooms = offices
        elif args['-l']:
            rooms = living_spaces
        else:
            rooms = offices + living_spaces
        if isinstance(rooms, str):
            print_info(rooms)
        else:
            pretty_print_data(rooms)

opt = docopt(__doc__, sys.argv[1:], True, 2.0)

if opt['--interactive']:
    print_header()
    amity = Amity()
    AmityInteractive().cmdloop()
