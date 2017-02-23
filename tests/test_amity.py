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
        for i in self.amity.rooms:
            self.assertIsInstance(i, Room)
        else:
            # The list should be empty
            self.assertEqual(len(self.amity.rooms), 0)

    def test_people_attr_is_list(self):
        self.assertIsInstance(self.amity.people, list)

    def test_people_attr_is_list_of_person_objs(self):
        for i in self.amity.people:
            self.assertIsInstance(i, Person)
        else:
            # The list should be empty
            self.assertEqual(len(self.amity.people), 0)


if __name__ == '__main__':
    unittest.main()

