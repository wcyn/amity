import unittest
from app.amity import Amity
from app.person import Person, Staff, Fellow
from app.room import Room, Office, LivingSpace


    
class TestAmity(unittest.TestCase):

    def setUp(self):
        self.amity = Amity()
        self.person = Person()
        self.staff = Staff()
        self.fellow = Fellow()
        self.room = Room()
        self.office = Office()
        self.living_space = LivingSpace()

    def tearDown(self):
        del self.amity
        del self.person 
        del self.staff 
        del self.fellow 
        del self.room 
        del self.office 
        del self.living_space 

    def test_rooms_attr_is_list(self):
        self.assertIsInstance(self.amity.rooms, list)

    def test_rooms_attr_is_list_of_room_objs(self):
        if self.amity.rooms:
            # To Avoid NoneType Error
            for i in self.amity.rooms:
                self.assertIsInstance(i, Room)
        else:
            self.assertIsInstance(self.amity.rooms, list)


    def test_people_attr_is_list(self):
        self.assertIsInstance(self.amity.people, list)

    def test_people_attr_is_list_of_person_objs(self):
        if self.amity.people:
            # To Avoid NoneType Error
            for i in self.amity.rooms:
                self.assertIsInstance(i, Person)
        else:
            self.assertIsInstance(self.amity.people, list)

    def test_create_room_returns_list_of_rooms(self):
        # Should return a list of Rooms
        rooms = self.amity.create_room(["hogwarts", "camelot"])
        self.assertIsInstance(rooms, list)
        self.assertNotEqual(len(rooms), 0)
        # And if it's not empty. Confirm that the items are Rooms
        if rooms:
            for i in rooms:
                self.assertIsInstance(i, Room) 

    def test_create_room_raises_value_error_for_non_string(self):
        with self.assertRaises(ValueError):
            self.amity.create_room([66.4, 34])

    def test_add_person_returns_person_object(self):
        person = self.amity.add_person("jane", "f", "y")
        self.assertIsInstance(person, Person)

    def test_add_person_raises_value_error_for_non_str_name(self):
        with self.assertRaises(ValueError):
            self.amity.add_person(23, "f", "y")

    def test_add_person_raises_value_error_for_non_str_type(self):
        with self.assertRaises(ValueError):
            self.amity.add_person("jane", 42, "y")

    def test_add_person_raises_value_error_for_non_str_accom(self):
        with self.assertRaises(ValueError):
            self.amity.add_person("jane", "s", 42)

    def test_add_person_accepts_valid_types(self):
        self.assertEqual(self.amity.add_person("jane", "random", "y"),
                              "Invalid person type")

    def test_add_person_accepts_valid_accommodation_opt(self):
        self.assertEqual(self.amity.add_person("jane", "f", "maybe"),
                              "Accomodation choice can only be y or n")



if __name__ == '__main__':
    unittest.main()

