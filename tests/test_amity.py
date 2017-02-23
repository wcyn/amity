import unittest

class TestAmity(unittest.TestCase):

    def test_rooms_attr_is_list(self):
        amity = Amity()
        self.assertIsInstance(amity.rooms, list)

    def test_rooms_attr_is_list_of_room_objs(self):
        amity = Amity()
        for i in amity.rooms:
            self.assertIsInstance(i, Room)
        else:
            # The list should be empty
            self.assertEqual(len(amity.rooms), 0)

    

