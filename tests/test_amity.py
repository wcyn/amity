import unittest

from app.amity import Amity
from app.person import Fellow, Person, Staff
from app.room import LivingSpace, Office, Room


class TestAmity(unittest.TestCase):

    def setUp(self):
        self.amity = Amity()
        self.staff = Staff("jane", "camelot")
        self.fellow = Fellow("jake", "occulus")
        self.office = Office("hogwarts")
        self.living_space = LivingSpace("python")
        self.people_list = self.amity.load_people("test_people.txt")
        self.rooms = ["gates", "page", "jobs"]
        self.amity.offices = [self.office]
        self.amity.living_spaces = [self.living_space]
        self.amity.fellows = [self.fellow]
        self.amity.staff = [self.staff]

    def tearDown(self):
        del self.amity
        del self.staff
        del self.fellow
        del self.office
        del self.living_space
        del self.people_list
        self.amity.offices = None
        self.amity.living_spaces = None
        self.amity.fellows = None
        self.amity.staff = None

    # Create Room Tests
    # *****************************

    def create_room_adds_rooms_to_amity_room_list(self):
        self.amity.create_room(self.rooms)
        room_objects = []
        for i in self.rooms:
            room_objects.append[Office(i)]
        self.assertEqual(self.amity.living_spaces, [
                         self.living_space] + room_objects)

    def create_room_adds_living_spaces_when_suffixed_with_ls(self):
        # Create room should return a list of created room objects
        bee = self.amity.create_room(["bee-ls"])
        self.assertEqual(self.amity.living_spaces, [self.living_space] + bee)

    def test_create_room_raises_type_error_with_non_string_room_names(self):
        with self.assertRaises(TypeError):
            rooms = [42, "gates", [42]]
            self.amity.create_room(rooms)

    def test_create_room_returns_error_message_when_no_room_provided(self):
        self.assertEqual(self.amity.error_codes[8], self.amity.create_room([]))

    def test_create_room_filters_out_duplicate_room_names(self):
        gates = self.amity.create_room(["gates", "gates"])
        self.assertEqual(self.amity.living_spaces, [self.living_space] + gates)

    def test_create_room_does_not_add_duplicate_room_name(self):
        self.amity.create_room(["python"])
        self.assertEqual(self.amity.living_spaces, [self.living_space])

    # Add Person tests
    # *****************************

    def test_add_person_fellow_adds_fellow_to_amity_list(self):
        janet = self.amity.add_person("Janet", "Fellow")
        self.assertEqual(self.amity.fellows, [self.fellow, janet])
        self.assertIsInstance(self.amity.fellows[-1], Fellow)

    def test_add_person_fellow_adds_fellow_object_with_all_valid_types(self):
        kate = self.amity.add_person("Kate", "f")
        jack = self.amity.add_person("Jack", "F")
        david = self.amity.add_person("David", "Fellow")
        maria = self.amity.add_person("Maria", "fellow")
        self.assertEqual(self.amity.fellows, [self.fellow, kate, jack,
                                              david, maria])

    def test_add_person_staff_adds_staff_to_amity_list(self):
        janet = self.amity.add_person("Janet", "Staff")
        self.assertEqual(self.amity.staff, [self.staff, janet])
        self.assertIsInstance(self.amity.staff[-1], Staff)

    def test_add_person_staff_adds_staff_object_with_all_valid_types(self):
        kate = self.amity.add_person("Kate", "f")
        jack = self.amity.add_person("Jack", "F")
        david = self.amity.add_person("David", "Staff")
        maria = self.amity.add_person("Maria", "staff")
        self.assertEqual(self.amity.staff, [self.staff, kate, jack,
                                            david, maria])

    def test_add_person_raises_type_error_with_non_string_person_name(self):
        with self.assertRaises(TypeError):
            self.amity.add_person(42, "Staff")

    def test_add_person_raises_type_error_for_non_str_type(self):
        with self.assertRaises(TypeError):
            self.amity.add_person("Jane", 42)

    def test_add_person_returns_error_message_if_type_is_invalid(self):
        self.assertEqual(self.amity.error_codes[5],
                         self.amity.add_person("Jane", "manager"))

    def test_add_person_returns_error_message_on_wrong_accommodation_option(self):
        self.assertEqual("%s %s" % (self.amity.error_codes[7], "please"),
                         self.amity.add_person("Jane", "manager", "please"))

    def test_add_person_staff_returns_staff_object(self):
        self.assertIsInstance(self.amity.add_person("Kate", "s"), Staff)

    def test_add_person_fellow_returns_fellow_object(self):
        self.assertIsInstance(self.amity.add_person("Kate", "f"), Fellow)

    def test_add_person_automatically_allocates_room_if_available(self):
        kate = self.amity.add_person("Kate", "f")
        jane = self.amity.add_person("Jane", "s")
        self.assertIsInstance(kate.allocated_office_space, Office)
        self.assertIsInstance(jane.allocated_office_space, Office)

    # Allocate Room to Person tests
    # *****************************

    def test_allocate_room_raises_attribute_error_for_non_person_object(self):
        with self.assertRaises(AttributeError):
            self.amity.allocate_room_to_person("person name", Room)

    def test_allocate_room_raises_attribute_error_for_non_room_object(self):
        with self.assertRaises(AttributeError):
            self.amity.allocate_room_to_person(self.fellow, "office name")

    def test_allocate_living_space_to_staff_gives_error_message(self):
        # Test that nothing is added to living spaces or offices
        staff = self.amity.allocate_room_to_person(
            self.staff, self.living_space)
        self.assertEqual(self.amity.living_spaces, [self.living_space])
        self.assertEqual(self.amity.error_codes[10], staff)

    def test_allocate_full_living_space_to_fellow_gives_error_message(self):
        self.living_space.num_of_occupants = self.living_space.max_occupants
        self.amity.allocate_room_to_person(self.fellow, self.living_space)
        self.assertEqual(self.amity.living_spaces, [self.living_space])
        self.assertEqual(self.amity.error_codes[11],
                         self.amity.allocate_room_to_person(
            self.fellow, self.living_space))

    def test_allocate_living_space_adds_living_space_object_to_person(self):
        # Returns the newly modified fellow object
        fellow = self.amity.allocate_room_to_person(
            self.fellow, self.living_space)
        self.assertIsInstance(fellow.allocated_living_space, LivingSpace)

    def test_allocate_living_space_adds_living_space_allocates_correct_living_space(self):
        # Returns the newly modified fellow object
        self.amity.allocate_room_to_person(
            self.fellow, self.living_space)
        self.assertEqual(self.fellow.allocated_living_space, self.living_space)

    def test_allocate_living_space_increments_number_of_occupants_in_living_space(self):
        self.amity.allocate_room_to_person(
            self.fellow, self.living_space)
        self.assertEqual(1, self.living_space.num_of_occupants)
        self.amity.allocate_room_to_person(
            self.fellow, self.living_space)
        self.assertEqual(2, self.living_space.num_of_occupants)

    def test_allocate_office_adds_living_space_allocates_correct_office(self):
        # Returns the newly modified fellow object
        self.amity.allocate_room_to_person(
            self.fellow, self.office)
        self.amity.allocate_room_to_person(
            self.staff, self.office)
        self.assertEqual(self.fellow.allocated_office_space, self.office)
        self.assertEqual(self.staff.allocated_office_space, self.office)

    def test_allocate_full_office_to_person_gives_error_message(self):
        self.office.num_of_occupants = self.office.max_occupants
        self.amity.allocate_room_to_person(self.fellow, self.office)
        self.amity.allocate_room_to_person(self.staff, self.office)
        self.assertEqual(self.amity.offices, [self.office])
        self.assertEqual(self.amity.error_codes[11], self.amity.allocate_room_to_person(self.fellow, self.office))
        self.assertEqual(self.amity.error_codes[11], self.amity.allocate_room_to_person(self.staff, self.office))

    def test_allocate_office_increments_number_of_occupants_in_office(self):
        self.amity.allocate_room_to_person(self.fellow, self.office)
        self.assertEqual(1, self.office.num_of_occupants)
        self.amity.allocate_room_to_person(self.fellow, self.office)
        self.assertEqual(2, self.office.num_of_occupants)

    # Reallocate Room to Person Tests
    # *******************************

    def test_reallocate_person_returns_error_message_when_person_does_not_exist(self):
        result = self.amity.reallocate_person("gavin", "hogwarts")
        self.assertEqual(result, self.amity.error_codes[2])

    def test_reallocate_person_returns_error_message_when_room_does_not_exist(self):
        result = self.amity.reallocate_person("jane", "rift")
        self.assertEqual(result, self.amity.error_codes[1])

    def test_reallocate_person_raises_type_error_with_non_string_person_name(self):
        with self.assertRaises(TypeError):
            self.amity.reallocate_person([], "hogwarts")

    def test_reallocate_person_raises_type_error_with_non_string_room_name(self):
        with self.assertRaises(TypeError):
            self.amity.reallocate_person("jane", 42)


    # Load People Tests
    # *****************************

    def test_load_people_raises_type_error_when_filename_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.load_people(42)

    def test_load_people_gives_error_message_when_file_doesnt_exist(self):
        result = self.amity.load_people("andelans.txt")
        self.assertEqual(result, self.amity.error_codes[12] + " 'andelans.txt'")

    def test_load_people_gives_error_message_when_file_is_empty(self):
        result = self.amity.load_people("empty.txt")
        self.assertEqual(result, self.amity.error_codes[13] + " 'empty.txt'")

    def test_load_people_gives_error_message_when_file_is_wrongly_formatted(self):
        result = self.amity.load_people("wrong_format.txt")
        self.assertEqual(result, self.amity.error_codes[14] + " 'wrong_format.txt'")

    def test_load_people_gives_error_message_when_filename_has_invalid_characters(self):
        result = self.amity.load_people("nairobi*.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.load_people("nairobi?.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.load_people("nairobi/.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.load_people("nairobi\.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")

    def test_load_people_loads_people_into_amity_data_variables(self):
        self.amity.load_people("people.in")
        self.assertEqual(5, len(self.amity.fellows))
        self.assertEqual(4, len(self.amity.staff))
        self.assertTrue([x for x in self.amity.fellows if x.name == "OLUWAFEMI SULE"])
        self.assertTrue([x for x in self.amity.fellows if x.name == "SIMON PATTERSON"])
        self.assertTrue([x for x in self.amity.fellows if x.name == "MARI LAWRENCE"])
        self.assertTrue([x for x in self.amity.fellows if x.name == "TANA LOPEZ"])
        self.assertTrue([x for x in self.amity.staff if x.name == "DOMINIC WALTERS"])
        self.assertTrue([x for x in self.amity.staff if x.name == "LEIGH RILEY"])
        self.assertTrue([x for x in self.amity.staff if x.name == "KELLY McGUIRE"])


    # *********************

    # Attributes Testing

    def test_rooms_attr_is_list(self):
        self.assertIsInstance(self.amity.rooms, list)

    def test_rooms_attribute_is_list_of_room_objects(self):
        if self.amity.rooms:
            # To Avoid NoneType Error
            for i in self.amity.rooms:
                self.assertIsInstance(i, Room)
        else:
            self.assertIsInstance(self.amity.rooms, list)

    def test_people_attr_is_list(self):
        self.assertIsInstance(self.amity.people, list)

    def test_people_attr_is_list_of_person_objects(self):
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
            for i in rooms:
                self.assertIsInstance(i, Room)

    def test_create_room_raises_value_error_for_non_string(self):
        with self.assertRaises(ValueError):
            self.amity.create_room([66.4, 34])

    def test_create_room_rejects_duplicate_name(self):
        self.assertEqual("A room already exists with this name",
                         self.amity.create_room(["krypton"]))

    # this tests for impossible case-not testable
    def test_new_person_obj_rejects_duplicate_id(self):
        self.person.id = 1
        person2 = Person("kelly", "hogwarts")
        self.assertEqual("A person with a similar ID exists",
                         person2.set_id(1))

    def test_add_person_raises_value_error_for_non_str_accom(self):
        with self.assertRaises(ValueError):
            self.amity.add_person("jane", "s", 42)

    def test_add_person_accepts_valid_types(self):
        self.assertEqual(self.amity.add_person("jane", "random", "y"),
                         "Invalid person type")

    def test_add_person_accepts_valid_accommodation_opt(self):
        self.assertEqual(self.amity.add_person("jane", "f", "maybe"),
                         "Accommodation choice can only be y or n")

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

    # needs more tests for random rooms
    def test_add_staff_assigns_office(self):
        # Should still create person even if no office space is available
        staff = self.amity.add_person("ken", "s")
        self.assertIsInstance(staff.get_allocated_office_space(), Office)

    def test_reallocate_person_returns_person_obj(self):
        office2 = Office("valhala")  # reduce number of people in a room  and
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
        self.assertEqual(4, len(self.amity.fellows))
        self.assertEqual(3, len(self.amity.staff))
        self.assertEqual(True, ["OLUWAFEMI SULE", "FELLOW", "Y"]
                         in self.amity.fellows)
        self.assertEqual(True, ["DOMINIC WALTERS", "STAFF"]
                         in self.amity.staff)
        self.assertEqual(True, ["SIMON PATTERSON", "FELLOW", "Y"]
                         in self.amity.fellows)
        self.assertEqual(True, ["MARI LAWRENCE", "FELLOW", "Y"]
                         in self.amity.fellows)
        self.assertEqual(True, ["LEIGH RILEY", "STAFF"]
                         in self.amity.staff)
        self.assertEqual(True, ["TANA LOPEZ", "FELLOW", "Y"]
                         in self.amity.fellows)
        self.assertEqual(True, ["KELLY McGUIRE", "STAFF"]
                         in self.amity.staff)

    def test_load_people_adds_people(self):
        people_names = [i.name for i in self.amity.people]
        self.assertEqual(True, "OLUWAFEMI SULE" in self.people_names)
        self.assertEqual(True, "DOMINIC WALTERS" in self.people_names)
        self.assertEqual(True, "SIMON PATTERSON" in self.people_names)
        self.assertEqual(True, "MARI LAWRENCE" in self.people_names)
        self.assertEqual(True, "LEIGH RILEY" in self.people_names)
        self.assertEqual(True, "TANA LOPEZ" in self.people_names)
        self.assertEqual(True, "KELLY McGUIRE" in self.people_names)

    def test_print_allocations(self):
        with self.amity.print_allocations() as (out, err):
            output = out.getvalue().strip()
            self.assertEqual(output)

if __name__ == '__main__':
    unittest.main()
