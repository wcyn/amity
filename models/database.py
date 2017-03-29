# coding=utf-8


class Database(object):
    """
    Holds the the databse commands for loading and saving data to SQLITE
    databases
    """
    @staticmethod
    def create_rooms_table(cursor):
        """
        Create Rooms Table in SQLITE Database
        :param cursor:
        :type cursor:
        """
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS rooms
                        (name varchar(50) PRIMARY KEY,
                        type varchar(15))
                        ''')
        return

    @staticmethod
    def create_people_table(cursor):
        """
        Create People Table in SQLITE Database
        :param cursor:
        :type cursor:
        """
        result = cursor.execute('''
                        CREATE TABLE IF NOT EXISTS people
                        (id INTEGER PRIMARY KEY,
                        first_name varchar(50) NOT NULL,
                        last_name varchar(50) NOT NULL,
                        role varchar(50),
                        allocated_office_space varchar(50),
                        allocated_living_space varchar(50),
                        wants_accommodation INTEGER DEFAULT 0)
                      ''')
        print("Result: ", result)
        return

    @staticmethod
    def insert_room_data(cursor, room_data):
        """
        Insert Room data into SQLITE Database
        :param cursor:
        :type cursor:
        :param room_data:
        :type room_data:
        """
        cursor.executemany(
            "INSERT OR REPLACE INTO rooms (name, "
            "type) values (?, ?)", room_data)

    @staticmethod
    def insert_people_data(cursor, people_data):
        """
        Insert Room data into SQLITE Database
        :param people_data:
        :type people_data:
        :param cursor:
        :type cursor:
        """
        cursor.executemany("INSERT OR REPLACE INTO people (id, "
                           "first_name, last_name, "
                           "role, allocated_office_space, "
                           "allocated_living_space, "
                           "wants_accommodation) values "
                           "(?, ?, ?, ?, ?, ?, ?)", people_data)

    @staticmethod
    def database_is_empty(cursor):
        """
        Check if database is empty or not
        :param cursor:
        :type cursor:
        """
        # Check if database is empty
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='people';")
        data = cursor.fetchall()
        cursor.execute("SELECT name FROM sqlite_master WHERE "
                       "type='table' AND name='rooms';")
        data += cursor.fetchall()
        if data:
            return False
        return True

    @staticmethod
    def get_all_people(cursor):
        """
        Check if database is empty or not
        :param cursor:
        :type cursor:
        """
        cursor.execute("SELECT * FROM people")
        return cursor.fetchall()

    @staticmethod
    def get_all_rooms(cursor):
        """
        Check if database is empty or not
        :param cursor:
        :type cursor:
        """
        cursor.execute("SELECT * FROM rooms")
        return cursor.fetchall()
