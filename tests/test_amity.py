import unittest

from app.amity import Amity
from app.person import Person, Staff, Fellow
from app.room import Room, Office, LivingSpace
    
class TestAmity(unittest.TestCase):

    def setUp(self):
        self.amity = Amity()
        self.staff = Staff("jane", "camelot")
        self.fellow = Fellow("jake", "oculus")
        self.office = Office("hogwarts")
        self.living_space = LivingSpace("python")
        self.people_list = self.amity.load_people("test_people.txt")

    def tearDown(self):
        del self.amity
        del self.person 
        del self.staff 
        del self.fellow 
        del self.room 
        del self.office 
        del self.living_space 
        del self.people_list

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
        rooms = self.amity.create_room(["mario", "luigi"])
        self.assertIsInstance(rooms, list)
        self.assertNotEqual(len(rooms), 0) 
        # What if only one was created
        # And if it's not empty. Confirm that the items are Rooms
        if rooms:
            for i in rooms: #
                self.assertIsInstance(i, Room) 

    def test_create_room_raises_value_error_for_non_string(self):
        with self.assertRaises(ValueError):
            self.amity.create_room([66.4, 34])

    def test_create_room_rejects_duplicate_name(self):
        self.assertEqual("A room already exists with this name",
                         self.amity.create_room(["krypton"]))

    def test_add_person_f_returns_fellow_object(self):
        self.assertIsInstance(self.amity.add_person("kate", "f", "y"), Fellow)

    def test_add_person_s_returns_staff_object(self):
        self.assertIsInstance(self.amity.add_person("kate", "s"), Staff)

#this tests for impossible case-not testable
    def test_new_person_obj_rejects_duplicate_id(self):
        self.person.id = 1
        person2 = Person("kelly", "hogwarts")
        self.assertEqual("A person with a similar ID exists",
                         person2.set_id(1))

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

    def test_add_fellow_returns_fellow_obj(self):
        fellow = self.amity.add_person("jane", "f", "y")
        self.assertIsInstance(fellow, Fellow)

    def test_add_staff_returns_staff_obj(self):
        staff = self.amity.add_person("jane", "s", "y")
        self.assertIsInstance(staff, Staff)

    def test_add_fellow_assigns_office(self):
        # needs more tests for random rooms
        # Should still create person even if no office space is available
        # these fellows should be added to the unallocated people list
        fellow = self.amity.add_person("jane", "f", "y")
        self.assertIsInstance(fellow.get_allocated_office_space(), Office)

    def test_add_staff_assigns_office(self): #needs more tests for random rooms
        # Should still create person even if no office space is available
        staff = self.amity.add_person("ken", "s")
        self.assertIsInstance(staff.get_allocated_office_space(), Office)

    def test_reallocate_person_returns_person_obj(self):
        office2 = Office("valhala") # reduce number of people in a room  and
        # increment new room
        self.assertIsInstance(self.amity.reallocate_person(
                                    self.person.id, office2.name), Person)

    def test_reallocate_person_office_works(self):
        office2 = Office("valhala")
        self.amity.reallocate_person(self.person.id, office2.name)
        self.assertEqual(office2.name,
                           self.person.allocated_office_space.name)

    def test_reallocate_fellow_living_space_works(self):
        living_space2 = LivingSpace("java")
        self.amity.reallocate_person(self.fellow.id, living_space2.name)
        self.assertEqual(living_space2.name,
                           self.fellow.allocated_office_space.name)

    def test_reallocate_person_fellow_office(self):
        office2 = Office("valhala")
        self.assertEqual(office2, self.amity.reallocate_person(
                            self.fellow.id, office2.name))

    def test_reallocate_person_raises_value_error_for_non_str_id(self):
        with self.assertRaises(ValueError):
            self.amity.reallocate_person(234, self.office.name)

    def test_reallocate_person_raises_value_error_for_non_str_name(self):
        with self.assertRaises(ValueError):
            self.amity.reallocate_person(self.person.id, 123)

    def test_load_people_returns_dict(self):
        self.assertIsInstance(self.people_list, dict)

    def test_load_people_works(self):
        # blank files?
        self.assertEqual(4, len(self.people_list["fellows"]))
        self.assertEqual(3, len(self.people_list["staff"]))
        self.assertEqual(True, ["OLUWAFEMI SULE", "FELLOW", "Y"] 
                         in self.people_list["fellows"])
        self.assertEqual(True, ["DOMINIC WALTERS", "STAFF"] 
                         in self.people_list["staff"])
        self.assertEqual(True, ["SIMON PATTERSON", "FELLOW", "Y"] 
                         in self.people_list["fellows"])
        self.assertEqual(True, ["MARI LAWRENCE", "FELLOW", "Y"] 
                         in self.people_list["fellows"])
        self.assertEqual(True, ["LEIGH RILEY", "STAFF"] 
                         in self.people_list["staff"])
        self.assertEqual(True, ["TANA LOPEZ", "FELLOW", "Y"] 
                         in self.people_list["fellows"])
        self.assertEqual(True, ["KELLY McGUIRE", "STAFF"] 
                         in self.people_list["staff"])        

    def test_load_people_adds_people(self):
        people_names = [i.name for i in self.amity.people]
        assertEqual(True, "OLUWAFEMI SULE" in self.people_names)
        assertEqual(True, "DOMINIC WALTERS" in self.people_names)
        assertEqual(True, "SIMON PATTERSON" in self.people_names)
        assertEqual(True, "MARI LAWRENCE" in self.people_names)
        assertEqual(True, "LEIGH RILEY" in self.people_names)
        assertEqual(True, "TANA LOPEZ" in self.people_names)
        assertEqual(True, "KELLY McGUIRE" in self.people_names)

    def test_print_allocations(self):
        with self.amity.print_allocations() as (out, err):
            output = out.getvalue().strip()
            self.assertEqual(output, )


if __name__ == '__main__':
    unittest.main()

