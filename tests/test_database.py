import sqlite3


class TestDataBase():
    def __init__(self, connection_string='test_database'):
        self.connection = sqlite3.connect(connection_string)