import unittest
import sqlite3
import uuid

from io import StringIO
from unittest.mock import patch, MagicMock,Mock

from app.amity import Amity
from app.person import Person, Fellow, Staff
from app.room import Room, LivingSpace, Office
from .test_database import TestDataBase


class TestAmity(unittest.TestCase):

    def setUp(self):
        self.amity = Amity()
        self.office = Office("hogwarts")
        self.living_space = LivingSpace("python")
        self.staff = Staff("jane", "surname")
        self.fellow = Fellow("jake", "surname")
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

    # Create Room Tests
    # *****************************

    def test_create_room_adds_rooms_to_amity_room_list(self):
        new_rooms = self.amity.create_room(self.rooms)
        self.assertEqual(self.amity.offices, [
            self.office] + new_rooms)

    def test_create_room_adds_living_spaces_when_suffixed_with_ls(self):
        # Create room should return a list of created room objects
        bee = self.amity.create_room(["bee-ls"])
        self.assertEqual(self.amity.living_spaces, [self.living_space] + bee)
        print(self.amity.living_spaces[1].__dict__)
        self.assertEqual(self.amity.living_spaces[1].name, "bee")

    def test_create_room_raises_type_error_with_non_string_room_names(self):
        with self.assertRaises(TypeError):
            rooms = [45, "gates", "room1"]
            self.amity.create_room(rooms)

    def test_create_room_returns_error_message_when_argument_not_list(self):
        self.assertEqual(self.amity.create_room("my room"), "Only a list of strings is allowed")
        # Assert that nothing has been added to LivingSpaces or Offices
        self.assertEqual(self.amity.living_spaces, [self.living_space])
        self.assertEqual(self.amity.offices, [self.office])

    def test_create_room_returns_error_message_when_no_room_provided(self):
        self.assertEqual(self.amity.error_codes[8], self.amity.create_room([]))

    def test_create_room_filters_out_duplicate_room_names(self):
        gates = self.amity.create_room(["gates", "gates"])
        self.assertEqual(len(self.amity.offices), 2)
        self.assertEqual(self.amity.offices, [self.office] + gates)

    def test_create_room_does_not_add_duplicate_room_name(self):
        result = self.amity.create_room(["python"])
        self.assertEqual(self.amity.living_spaces, [self.living_space])
        self.assertEqual(self.amity.error_codes[3] + " 'python'", result)

    # Add Person tests
    # *****************************

    def test_add_person_fellow_adds_fellow_to_amity_list(self):
        janet = self.amity.add_person("Janet","surname", "Fellow")
        self.assertEqual(self.amity.fellows, [self.fellow, janet])
        self.assertIsInstance(self.amity.fellows[-1], Fellow)

    def test_add_person_fellow_adds_fellow_object_with_all_valid_types(self):
        kate = self.amity.add_person("Kate", "surname", "f")
        jack = self.amity.add_person("Jack", "surname", "F")
        david = self.amity.add_person("David", "surname", "Fellow")
        maria = self.amity.add_person("Maria", "surname", "fellow")
        self.assertEqual(self.amity.fellows, [self.fellow, kate, jack,
                                              david, maria])

    def test_add_person_staff_adds_staff_to_amity_list(self):
        janet = self.amity.add_person("Janet", "surname", "Staff")
        self.assertEqual(self.amity.staff, [self.staff, janet])
        self.assertIsInstance(self.amity.staff[-1], Staff)

    def test_add_person_staff_adds_staff_object_with_all_valid_types(self):
        kate = self.amity.add_person("Kate", "surname", "s")
        jack = self.amity.add_person("Jack", "surname", "S")
        david = self.amity.add_person("David", "surname", "Staff")
        maria = self.amity.add_person("Maria", "surname", "staff")
        self.assertEqual(self.amity.staff, [self.staff, kate, jack,
                                            david, maria])

    def test_add_person_raises_attribute_error_with_non_string_person_name(self):
        with self.assertRaises(AttributeError):
            self.amity.add_person(42, "surname", "Staff")

    def test_add_person_raises_attribute_error_for_non_str_type(self):
        with self.assertRaises(AttributeError):
            self.amity.add_person("Jane", "surname", 42)

    def test_add_person_returns_error_message_if_type_is_invalid(self):
        self.assertEqual(self.amity.error_codes[5] + " 'manager'",
                         self.amity.add_person("Jane", "surname", "manager"))

    def test_add_person_returns_error_message_on_wrong_accommodation_option(self):
        self.assertEqual("%s %s" % (self.amity.error_codes[7], "'please'"),
                         self.amity.add_person("Jane", "surname", "staff", "please"))

    def test_add_person_staff_returns_staff_object(self):
        self.assertIsInstance(self.amity.add_person("Kate", "surname", "s"), Staff)

    def test_add_person_fellow_returns_fellow_object(self):
        self.assertIsInstance(self.amity.add_person("Kate", "surname", "f"), Fellow)

    def test_add_person_automatically_allocates_room_if_available(self):
        kate = self.amity.add_person("Kate", "surname", "f")
        jane = self.amity.add_person("Jane", "surname", "s")
        self.assertIsInstance(kate.allocated_office_space, Office)
        self.assertIsInstance(jane.allocated_office_space, Office)

    # Allocate Room to Person tests
    # *****************************

    def test_allocate_room_raises_attribute_error_for_non_person_object(self):
        with self.assertRaises(AttributeError):
            self.amity.allocate_room_to_person("person name", self.office)

    def test_allocate_room_raises_attribute_error_for_non_room_object(self):
        with self.assertRaises(AttributeError):
            self.amity.allocate_room_to_person("office name", self.fellow)

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

    def test_allocate_living_space_adds_living_space_object_to_fellow(self):
        # Returns the newly modified fellow object
        fellow = self.amity.allocate_room_to_person(
            self.fellow, self.living_space)
        self.assertIsInstance(fellow.allocated_living_space, LivingSpace)

    def test_allocate_living_space_allocates_correct_living_space(self):
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

    def test_allocate_room_returns_transfer_message_if_person_already_has_room(self):
        office2 = Office("krypton")
        self.fellow.allocated_office_space = self.office
        result = self.amity.allocate_room_to_person(self.fellow, office2)
        self.assertEqual(result, "About to move %s from %s to %s" %(self.fellow.first_name,
                                                                    self.office.name, office2.name))

    # def test_allocate_person_decrements_num_of_occupants_in_previous_room_if_person_previously_allocated(self):

    # Reallocate Room to Person Tests
    # *******************************

    def test_reallocate_person_raises_type_error_when_id_not_uuid(self):
        with self.assertRaises(IndexError):
            self.amity.reallocate_person(self.fellow.id, "hogwarts")

    def test_reallocate_person_returns_error_message_when_room_does_not_exist(self):
        result = self.amity.reallocate_person(self.amity.fellows[0], "rift")
        self.assertEqual(result, self.amity.fellows[0])

    def test_reallocate_person_raises_attribute_error_with_non_person_object_ie_list(self):
        with self.assertRaises(AttributeError):
            self.amity.reallocate_person([], "hogwarts")

    def test_reallocate_person_raises_type_error_with_non_integer_person_id_ie_string(self):
        with self.assertRaises(AttributeError):
            self.amity.reallocate_person("jane", "hogwarts")

    def test_reallocate_person_raises_type_error_with_non_string_room_name(self):
        with self.assertRaises(TypeError):
            self.amity.reallocate_person(self.amity.fellows[0], 42)


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

    # Print Allocations Tests
    # *****************************

    def test_print_allocations_raises_type_error_when_filename_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.print_allocations(42)

    def test_print_allocations_gives_error_message_when_file_doesnt_exist(self):
        result = self.amity.print_allocations("andelans.txt")
        self.assertEqual(result, self.amity.error_codes[12] + " 'andelans.txt'")

    def test_print_allocations_gives_error_message_when_filename_has_invalid_characters(self):
        result = self.amity.print_allocations("nairobi*.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.print_allocations("nairobi?.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.print_allocations("nairobi/.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.print_allocations("nairobi\.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")

    def test_print_allocations_prints_only_allocated_people_to_file(self):
        Fellow("Vader") # Unallocated
        self.amity.allocate_room_to_person(self.living_space, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.staff)

        filename = "empty.txt"
        self.amity.print_allocations(filename)
        with open(filename) as f:
            unallocated = f.readlines()
        # Get rid of newlines
        unallocated = [x.strip() for x in unallocated]
        self.assertTrue("Jane Staff Camelot" in unallocated)
        self.assertTrue("Jake Fellow Occulus" in unallocated)
        self.assertTrue("Jake Fellow Camelot" in unallocated)
        self.assertFalse("Vader Fellow" in unallocated)

    def test_print_allocations_prints_correctly_to_console_if_no_file_given(self):
        self.amity.allocate_room_to_person(self.living_space, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.staff)
        allocated = "Jane Staff Camelot\n" \
                    "Jake Fellow Occulus\n" \
                    "Jake Fellow Camelot"
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            # print("hello world")
            self.amity.print_allocations()
            self.assertEqual(fakeOutput.getvalue().strip(), allocated)

    # Print Unallocated Tests
    # *****************************

    def test_print_unallocated_raises_type_error_when_filename_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.print_unallocated(42)

    def test_print_unallocated_gives_error_message_when_file_doesnt_exist(self):
        result = self.amity.print_unallocated("andelans.txt")
        self.assertEqual(result, self.amity.error_codes[12] + " 'andelans.txt'")

    def test_print_unallocated_gives_error_message_when_filename_has_invalid_characters(self):
        result = self.amity.print_unallocated("nairobi*.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.print_unallocated("nairobi?.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.print_unallocated("nairobi/.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")
        result = self.amity.print_unallocated("nairobi\.txt")
        self.assertEqual(result, self.amity.error_codes[15] + " 'nairobi*.txt'")

    def test_print_unallocated_prints_only_unallocated_people_to_file(self):
        Fellow("Vader") # Unallocated
        Staff("Malia")  # Unallocated
        self.amity.allocate_room_to_person(self.living_space, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.staff)

        filename = "empty.txt"
        self.amity.print_unallocated(filename)
        with open(filename) as f:
            unallocated = f.readlines()
        # Get rid of newlines
        unallocated = [x.strip() for x in unallocated]
        self.assertFalse("Jane Staff Camelot" in unallocated)
        self.assertFalse("Jake Fellow Occulus" in unallocated)
        self.assertFalse("Jake Fellow Camelot" in unallocated)
        self.assertTrue("Vader Fellow" in unallocated)
        self.assertTrue("Malia Staff" in unallocated)


    def test_print_unallocated_prints_correctly_to_console_if_no_file_given(self):
        Fellow("Vader")  # Unallocated
        Staff("Malia")  # Unallocated
        self.amity.allocate_room_to_person(self.living_space, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.staff)
        unallocated = "Vader Fellow\n" \
                      "Malia Staff"
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            self.amity.print_unallocated()
            self.assertEqual(fakeOutput.getvalue().strip(), unallocated)

    # Print Room Tests
    # *****************************

    def test_print_room_raises_type_error_when_room_name_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.print_room(42)

    def test_print_room_gives_error_message_when_room_doesnt_exist(self):
        result = self.amity.print_room("parliament")
        self.assertEqual(result, self.amity.error_codes[1] + ": 'parliament'")

    def test_print_room_gives_informative_message_when_room_is_empty(self):
        result = self.amity.print_room("hogwarts")
        self.assertEqual(result, self.amity.error_codes[16] + ": 'hogwarts'")

    def test_print_room_prints_only_the_people_in_the_room_to_console(self):
        Fellow("Vader")  # Unallocated
        Staff("Malia")  # Unallocated
        self.amity.allocate_room_to_person(self.living_space, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.fellow)
        self.amity.allocate_room_to_person(self.office, self.staff)
        office_occupants = "Jake Fellow\n" \
                            "Jane Staff"
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            self.amity.print_room("hogwarts")
            self.assertEqual(fakeOutput.getvalue().strip(), office_occupants)

    # Save State Tests
    # *****************************

    def test_save_state_raises_type_error_when_database_name_not_string_ie_number(self):
        with self.assertRaises(TypeError):
            self.amity.save_state(42)

    def test_save_state_raises_type_error_when_database_name_not_string_ie_list(self):
        with self.assertRaises(TypeError):
            self.amity.save_state(["hello"])

    def test_save_state_gives_asks_for_override_when_database_already_exists(self):
        sqlite3.connect = MagicMock(return_value="Would you like to override the database" + " 'test_database'?")
        result = self.amity.save_state("test_database")
        self.assertEqual(result, "About to override database" + " 'test_database'")

    def test_save_state_gives_informative_message_when_no_data_to_save(self):
        self.amity.offices = []
        self.amity.living_spaces = []
        self.amity.fellows = []
        self.amity.staff = []
        self.people_list = []

        sqlite3.connect = MagicMock(return_value='No data to save')
        result = self.amity.save_state("test_database")
        self.assertEqual(result, "No data to save")

    def test_save_state_sqlite3_connect_success(self):
        sqlite3.connect = MagicMock(return_value='connection succeeded')
        result = self.amity.save_state("test_database")
        sqlite3.connect.assert_called_with("test_database")
        print("Connection succeed: ", result)
        self.assertEqual(result, 'connection succeeded')

    def test_save_state_sqlite3_connect_fail_on_invalid_characters(self):
        sqlite3.connect = MagicMock(return_value='connection failed')
        result = self.amity.save_state('test_database/')
        self.assertEqual(result, self.amity.error_codes[17] + " 'test_database/'")
        result = self.amity.save_state('test_database*')
        self.assertEqual(result, self.amity.error_codes[17] + " 'test_database*'")

    # Load State Tests
    # *****************************

    def test_load_state_raises_type_error_when_database_name_not_string_ie_number(self):
        with self.assertRaises(TypeError):
            self.amity.load_state(42)

    def test_load_state_raises_type_error_when_database_name_not_string_ie_list(self):
        with self.assertRaises(TypeError):
            self.amity.load_state(["hello"])

    def test_load_state_gives_informative_message_when_no_database_is_empty(self):
        self.amity.offices = []
        self.amity.living_spaces = []
        self.amity.fellows = []
        self.amity.staff = []
        self.people_list = []

        sqlite3.connect = MagicMock(return_value="No data to Load. Empty database 'test_database'")
        result = self.amity.load_state("test_database")
        self.assertEqual(result, "No data to Load. Empty database 'test_database'")

    def test_load_state_sqlite3_connect_fail_on_invalid_characters(self):
        sqlite3.connect = MagicMock(return_value='connection failed')
        result = self.amity.load_state('test_database/')
        self.assertEqual(result, self.amity.error_codes[17] + " 'test_database/'")
        result = self.amity.load_state('test_database*')
        self.assertEqual(result, self.amity.error_codes[17] + " 'test_database*'")


if __name__ == '__main__':
    unittest.main()
