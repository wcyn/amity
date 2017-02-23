import unittest


class TestAmity(unittest.TestCase):
    amity = Amity()

    def test_rooms_attr_is_list(self):
        self.assertIsInstance(amity.rooms, list)

    def test_rooms_attr_is_list_of_room_objs(self):
        for i in amity.rooms:
            self.assertIsInstance(i, Room)
        else:
            # The list should be empty
            self.assertEqual(len(amity.rooms), 0)

    def test_people_attr_is_list(self):
        self.assertIsInstance(amity.people, list)

    def test_people_attr_is_list_of_person_objs(self):
        for i in amity.people:
            self.assertIsInstance(i, Person)
        else:
            # The list should be empty
            self.assertEqual(len(amity.people), 0)

