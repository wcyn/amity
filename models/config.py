# coding=utf-8
import sys


class Config(object):
    """
        Holds Configuration data for the amity application
    """
    out = sys.stdout
    database_directory = '../databases'
    files_directory = '../files'
    default_db_name = '*amity_database'
    empty_database = "*amity_empty"
    special_databases = [default_db_name, empty_database]

    allowed_fellow_strings = ["fellow", "f"]
    allowed_staff_strings = ["staff", "s"]
    allowed_office_strings = ["office", "o"]
    allowed_living_space_strings = ["living_space", "ls", "living-space", "l"]
    allowed_yes_strings = ["yes", "y"]
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
        10: "Cannot allocate a living space to staff member",
        11: "Cannot add person. The room is fully occupied",
        12: "Cannot find the file",
        13: "The file is empty",
        14: "Wrongly formatted file",
        15: "Invalid characters in the filename",
        16: "The room is empty",
        17: "Invalid character(s) in the database name",
        18: "Non-existent database"
    }
