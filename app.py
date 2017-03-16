#!/usr/bin/env python

"""
Amity.
A room allocation system for Fellows and Staff.

Usage:
    app.py create_room <room_name>...
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
    <room_name>           The name of the room to be created or printed. Add '-ls' at the end of the room name to
                          indicate that it is a living space. Default is office
    <first_name>          The first name of the Fellow or Staff
    <last_name>           The last name of the Fellow or Staff
    <role>                The role of the new person, either Fellow or Staff
    <wants_accommodation> Indication of if the Fellow wants accommodation or not. Choices ('N','No', 'Yes','Y')
    <person_identifier>   A Unique User identifier of the Fellow or Staff
    <new_room_name>       The Room name to which the Fellow or Staff is to be reallocated
    <filename>            The file to load from or save data to
    <sqlite_database>     The database to load from or save data to

Options:
    -i --interactive        Interactive Mode
    -h --help               Show this screen and exit from amity
    --o FILENAME            Specify filename
    --db sqlite_databse     Name of SQLite Database to load from or save data to
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

def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action
    """
    def fn(self, args):
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
    '''
        Create a header to be displayed when the program starts
    '''
    os.system("clear")
    print("\n")
    cprint(figlet_format('AMITY', font='colossal'), 'blue')
    cprint('-' * 52, 'blue')
    cprint("%sA ROOM ALLOCATION SYSTEM." % (" " * 14), 'cyan')
    # cprint("\nType 'help' to see the list of available commands\n", 'grey')


def pretty_print_data(list_of_dicts):
    key_list = [colored(key.title().split('__')[-1], 'magenta')  for key in list_of_dicts[0].keys()]
    table_rows = [key_list]
    d = {}
    for object in list_of_dicts:
        row_data = []
        for key, value in object.items():
            row_data.append(colored(value, 'blue'))
        table_rows.append(row_data)
    table = AsciiTable(table_rows)
    cprint(table.table, 'magenta')


class AmityInteractive(cmd.Cmd):
    '''
        The Amity Command Line Interface to be used for User interaction
    '''
    intro = colored("\nWelcome to my Amity!" \
            + "\n\t<Type 'help' to see the list of available commands>\n", 'blue', attrs=['dark'])

    amity_prompt = colored('Amity # ', 'cyan', attrs=['bold'])
    prompt = amity_prompt


    def do_quit(self, args):
        """ Quits Amity """
        print("Ciao!")
        exit()


opt = docopt(__doc__, sys.argv[1:])

if opt['--interactive']:
    print_header()
    amity = Amity()
    AmityInteractive().cmdloop()