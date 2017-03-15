import unittest
import sqlite3
import os

from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock,Mock

from app.amity import Amity
from app.person import Fellow, Staff
from app.room import LivingSpace, Office


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
        self.assertEqual(self.amity.living_spaces[1].name, "Bee")

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
        self.assertEqual(self.amity.offices, [self.office])
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
        fellow2 = Fellow("Maria", "Jones")
        self.amity.allocate_room_to_person(
            fellow2, self.living_space)
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
        self.amity.allocate_room_to_person(self.staff, self.office)
        self.assertEqual(2, self.office.num_of_occupants)

    def test_allocate_room_returns_transfer_message_if_person_already_has_room(self):
        office2 = Office("krypton")
        self.fellow.allocated_office_space = self.office
        result = self.amity.allocate_room_to_person(self.fellow, office2)
        self.assertEqual(result, "About to move %s from %s to %s" %(self.fellow.first_name,
                                                                    self.office.name, office2.name))

    def test_allocate_person_causes_decrement_in_num_of_occupants_in_office_space_if_staff_previously_allocated(self):
        office2 = Office("krypton")
        self.assertEqual(0, office2.num_of_occupants)
        self.assertEqual(0, self.office.num_of_occupants)
        self.staff.allocated_office_space = self.office
        self.assertEqual(1, self.office.num_of_occupants)

        staff = self.amity.allocate_room_to_person(self.staff, office2, True)

        self.assertEqual(1, office2.num_of_occupants)
        self.assertEqual(0, self.office.num_of_occupants)
        self.assertEqual(office2, self.staff.allocated_office_space)
        self.assertEqual(office2, staff.allocated_office_space)

    def test_allocate_person_causes_decrement_in_num_of_occupants_in_living_space_if_fellow_previously_allocated(self):
        living_space2 = LivingSpace("krypton")
        self.assertEqual(0, living_space2.num_of_occupants)
        self.assertEqual(0, self.living_space.num_of_occupants)
        self.fellow.allocated_living_space = self.living_space
        self.assertEqual(1, self.living_space.num_of_occupants)

        fellow = self.amity.allocate_room_to_person(self.fellow, living_space2, True)

        self.assertEqual(1, living_space2.num_of_occupants)
        self.assertEqual(0, self.living_space.num_of_occupants)
        self.assertEqual(living_space2, self.fellow.allocated_living_space)
        self.assertEqual(living_space2, fellow.allocated_living_space)


    # Randomly Allocate Room Tests
    # *****************************

    def test_randomly_allocate_room_returns_error_message_if_room_type_is_invalid(self):
        self.assertEqual(self.amity.error_codes[6] + " 'mansion'",
                         self.amity.randomly_allocate_room(self.fellow, "mansion"))

    def test_randomly_allocate_room_assigns_correct_room_type(self):
        ls_result = self.amity.randomly_allocate_room(self.fellow, "ls")
        o_result = self.amity.randomly_allocate_room(self.fellow, "o")
        self.assertIsInstance(ls_result, LivingSpace)
        self.assertIsInstance(o_result, Office)
        self.assertEqual(ls_result, self.fellow.allocated_living_space)
        self.assertEqual(o_result, self.fellow.allocated_office_space)

    def test_randomly_allocate_room_does_not_assign_full_room(self):
        self.office.num_of_occupants = self.office.max_occupants
        o_result = self.amity.randomly_allocate_room(self.fellow, "o")
        self.assertEqual(o_result, None)
        self.assertEqual(self.fellow.allocated_office_space, None)


    # Load People Tests
    # *****************************

    def test_load_people_raises_OS_error_when_filename_not_is_integer(self):
        with self.assertRaises(OSError):
            self.amity.load_people(42)

    def test_load_people_raises_type_error_when_filename_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.load_people([])

    def test_load_people_gives_error_message_when_file_doesnt_exist(self):
        filename = "test_no_exist.txt"
        if os.path.isfile(filename):
            os.remove(filename)
        result = self.amity.load_people(filename)
        self.assertEqual(result, self.amity.error_codes[12] + " '%s'" % filename)


    def test_load_people_gives_error_message_when_file_is_empty(self):
        filename = "test_empty.txt"
        # Create empty text file
        file = open(filename, 'w')
        file.close()
        result = self.amity.load_people(filename)
        self.assertEqual(result, self.amity.error_codes[13] + " '%s'" % filename)
        os.remove(filename)

    def test_load_people_gives_error_message_when_file_is_wrongly_formatted(self):
        filename = "wrong_format.txt"
        lines = ["Wrongly formatted\n", "File that should\n", "cause an error when loaded\n", "in Amity."]
        # Create wrongly formatted file
        with open(filename, 'w') as f:
            f.writelines(lines)

        result = self.amity.load_people(filename)
        self.assertEqual(result, self.amity.error_codes[14] + " '%s'" % filename)
        os.remove(filename) # Finally remove the file

    def test_load_people_loads_people_into_amity_data_variables(self):
        filename = "test_people.in"
        self.amity.load_people("files/" + filename)
        print("\n\n **** Amity fellows: ",  self.amity.fellows)
        self.assertEqual(5, len(self.amity.fellows))
        self.assertEqual(4, len(self.amity.staff))
        for i in self.amity.fellows:
            print("Fellow: ", i.__dict__)

        self.assertTrue([x for x in self.amity.fellows if x.first_name.lower() + " " + x.last_name.lower() ==
                         "OLUWAFEMI SULE".lower()])
        self.assertTrue([x for x in self.amity.fellows if x.first_name.lower() + " " + x.last_name.lower() ==
                         "SIMON PATTERSON".lower()])
        self.assertTrue([x for x in self.amity.fellows if x.first_name.lower() + " " + x.last_name.lower() ==
                         "MARI LAWRENCE".lower()])
        self.assertTrue([x for x in self.amity.fellows if x.first_name.lower() + " " + x.last_name.lower() ==
                         "TANA LOPEZ".lower()])
        self.assertTrue([x for x in self.amity.staff if x.first_name.lower() + " " + x.last_name.lower() ==
                         "DOMINIC WALTERS".lower()])
        self.assertTrue([x for x in self.amity.staff if x.first_name.lower() + " " + x.last_name.lower() ==
                         "LEIGH RILEY".lower()])
        self.assertTrue([x for x in self.amity.staff if x.first_name.lower() + " " + x.last_name.lower() ==
                         "KELLY McGUIRE".lower()])

    # Print Allocations Tests
    # *****************************

    def test_print_allocations_raises_type_error_when_filename_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.print_allocations(42)
            self.amity.print_allocations(["hello"])


    def test_print_allocations_gives_message_when_no_data_to_print(self):
        result = self.amity.print_allocations("test_allocations.txt")
        self.assertEqual(result['message'], "No allocations to print")

    def test_print_allocations_ignores_invalid_characters_in_filename(self):
        filename = "test_nairobi.txt"
        result = self.amity.print_allocations("test_nairobi:.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi*.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi?.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi<.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi>.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi/.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi\.txt")
        self.assertEqual(result['filename'], filename)
        os.remove(filename)

    def test_print_allocations_prints_only_allocated_people_to_file(self):
        fellow = Fellow("Vader", "Surname")
        fellow.allocated_office_space, fellow.allocated_living_space = None, None
        self.amity.fellows.append(fellow)  # Unallocated

        self.fellow.allocated_living_space = self.living_space
        self.fellow.allocated_office_space = self.office
        self.staff.allocated_office_space = self.office

        filename = "test_allocations.txt"
        self.amity.print_allocations(filename)
        with open(filename) as f:
            allocated = f.readlines()
        # Get rid of newlines
        allocated = [x.strip() for x in allocated]
        self.assertTrue("Jane Surname Staff Hogwarts" in allocated)
        self.assertTrue("Jake Surname Fellow Hogwarts Python" in allocated)
        self.assertFalse("Vader Surname Fellow" in allocated)
        os.remove(filename)

    def test_print_allocations_prints_fellows_with_either_both_or_one_allocation_present(self):
        fellow = Fellow("Vader", "Surname")
        fellow2 = Fellow("Alex", "Surname")
        fellow3 = Fellow("David", "Surname")
        staff = Staff("Malia", "Surname")
        fellow.allocated_office_space, fellow.allocated_living_space = None, None
        fellow2.allocated_office_space, fellow2.allocated_living_space = self.office, None
        fellow3.allocated_office_space, fellow3.allocated_living_space = None, self.living_space
        staff.allocated_office_space = None

        self.amity.fellows.append(fellow) # Unallocated
        self.amity.fellows.append(fellow2) # Unallocated
        self.amity.fellows.append(fellow3) # Unallocated
        self.amity.staff.append(staff)  # Unallocated
        self.fellow.allocated_living_space =  self.living_space
        self.fellow.allocated_office_space = self.office
        self.staff.allocated_office_space = self.office

        filename = "allocated.txt"
        self.amity.print_allocations(filename)
        with open(filename) as f:
            allocated = f.readlines()

        # Get rid of newlines
        allocated = [x.strip() for x in allocated]
        self.assertTrue("Jane Surname Staff Hogwarts" in allocated)
        self.assertTrue("Jake Surname Fellow Hogwarts Python" in allocated)
        self.assertTrue("Alex Surname Fellow Hogwarts -" in allocated)
        self.assertTrue("David Surname Fellow - Python" in allocated)
        self.assertFalse("Malia Surname Staff" in allocated)
        self.assertFalse("Vader Surname Fellow" in allocated)
        os.remove(filename)

    def test_print_allocations_prints_correctly_to_console_if_no_file_given(self):
        self.amity.allocate_room_to_person(self.fellow, self.living_space)
        self.amity.allocate_room_to_person(self.fellow, self.office)
        self.amity.allocate_room_to_person(self.staff, self.office)
        allocated = "Jane Surname Staff Hogwarts\n" \
                    "Jake Surname Fellow Hogwarts Python"
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            self.amity.print_allocations()
            self.assertEqual(fakeOutput.getvalue().strip(), allocated)

    # Print Unallocated Tests
    # *****************************

    def test_print_unallocated_raises_type_error_when_filename_not_string(self):
        with self.assertRaises(TypeError):
            self.amity.print_unallocated(42)
            self.amity.print_allocations(["hello"])

    def test_print_unallocated_ignores_invalid_characters_in_filename(self):
        filename = "test_nairobi.txt"
        result = self.amity.print_allocations("test_nairobi:.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi*.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi?.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi<.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi>.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi/.txt")
        self.assertEqual(result['filename'], filename)
        result = self.amity.print_allocations("test_nairobi\.txt")
        self.assertEqual(result['filename'], filename)
        os.remove(filename)

    def test_print_unallocated_prints_only_unallocated_people_to_file(self):
        fellow = Fellow("Vader", "Surname")
        staff = Staff("Malia", "Surname")
        fellow.allocated_office_space, fellow.allocated_living_space = None, None
        staff.allocated_office_space = None
        self.amity.fellows.append(fellow)  # Unallocated
        self.amity.staff.append(staff)  # Unallocated
        self.fellow.allocated_living_space = self.living_space
        self.fellow.allocated_office_space = self.office
        self.staff.allocated_office_space = self.office

        filename = "unallocated.txt"
        self.amity.print_unallocated(filename)
        with open(filename) as f:
            unallocated = f.readlines()
        # Get rid of newlines
        unallocated = [x.strip() for x in unallocated]
        self.assertFalse("Jane Surname Staff Hogwarts" in unallocated)
        self.assertFalse("Jake Surname Fellow Hogwarts Python" in unallocated)
        self.assertTrue("Malia Surname Staff" in unallocated)
        self.assertTrue("Vader Surname Fellow" in unallocated)
        os.remove(filename)

    def test_print_unallocated_prints_fellows_with_either_both_or_one_allocation_missing(self):
        fellow = Fellow("Vader", "Surname")
        fellow2 = Fellow("Alex", "Surname")
        fellow3 = Fellow("David", "Surname")
        staff = Staff("Malia", "Surname")
        fellow.allocated_office_space, fellow.allocated_living_space = None, None
        fellow2.allocated_office_space, fellow2.allocated_living_space = self.office, None
        fellow3.allocated_office_space, fellow3.allocated_living_space = None, self.living_space
        staff.allocated_office_space = None

        self.amity.fellows.append(fellow) # Unallocated
        self.amity.fellows.append(fellow2) # Unallocated
        self.amity.fellows.append(fellow3) # Unallocated
        self.amity.staff.append(staff)  # Unallocated
        self.fellow.allocated_living_space =  self.living_space
        self.fellow.allocated_office_space = self.office
        self.staff.allocated_office_space = self.office

        filename = "unallocated.txt"
        self.amity.print_unallocated(filename)
        with open(filename) as f:
            unallocated = f.readlines()
        # Get rid of newlines
        unallocated = [x.strip() for x in unallocated]
        self.assertFalse("Jane Surname Staff Hogwarts" in unallocated)
        self.assertFalse("Jake Surname Fellow Hogwarts Python" in unallocated)
        self.assertTrue("Malia Surname Staff" in unallocated)
        self.assertTrue("Vader Surname Fellow" in unallocated)
        self.assertTrue("Alex Surname Fellow Hogwarts -" in unallocated)
        self.assertTrue("David Surname Fellow - Python" in unallocated)
        os.remove(filename)


    def test_print_unallocated_prints_correctly_to_console_if_no_file_given(self):
        fellow = Fellow("Vader", "Surname")
        fellow2 = Fellow("Alex", "Surname")
        fellow3 = Fellow("David", "Surname")
        staff = Staff("Malia", "Surname")
        fellow.allocated_office_space, fellow.allocated_living_space = None, None
        fellow2.allocated_office_space, fellow2.allocated_living_space = self.office, None
        fellow3.allocated_office_space, fellow3.allocated_living_space = None, self.living_space
        staff.allocated_office_space = None

        self.amity.fellows.append(fellow)  # Unallocated
        self.amity.fellows.append(fellow2)  # Unallocated
        self.amity.fellows.append(fellow3)  # Unallocated
        self.amity.staff.append(staff)  # Unallocated
        self.fellow.allocated_living_space = self.living_space
        self.fellow.allocated_office_space = self.office
        self.staff.allocated_office_space = self.office

        unallocated = "Malia Surname Staff\n" \
                        "Vader Surname Fellow\n"\
                        "David Surname Fellow - Python\n"\
                        "Alex Surname Fellow Hogwarts -"
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
        fellow = Fellow("Vader", "Surname")
        staff = Staff("Malia", "Surname")
        fellow.allocated_office_space, fellow.allocated_living_space = None, None
        staff.allocated_office_space = None

        self.amity.fellows.append(fellow)  # Unallocated
        self.amity.staff.append(staff)  # Unallocated
        self.fellow.allocated_living_space = self.living_space
        self.fellow.allocated_office_space = self.office
        self.staff.allocated_office_space = self.office

        office_occupants = "Jane Surname Staff\n" \
                           "Jake Surname Fellow"
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
        database_name = "test_database_override"
        # Create temporary database
        db_file = self.amity.database_directory + database_name
        res = sqlite3.connect(db_file)
        print("\n\n %%%% res: ", res)
        sqlite3.connect = MagicMock(return_value="About to override database '%s'" % database_name)
        result = self.amity.save_state(database_name)
        self.assertEqual(result, "About to override database" + " '%s'" % database_name)
        db_path = Path(db_file)
        if db_path.is_file():
            os.remove(self.amity.database_directory + database_name)

    def test_save_state_gives_informative_message_when_no_data_to_save(self):
        self.amity.offices = []
        self.amity.living_spaces = []
        self.amity.fellows = []
        self.amity.staff = []
        self.people_list = []

        sqlite3.connect = MagicMock(return_value='No data to save')
        result = self.amity.save_state("test_database_no_data")
        print("result: ", result)
        self.assertEqual(result, "No data to save")

    def test_save_state_sqlite3_connect_success(self):
        database_name = "test_database_success"
        sqlite3.connect = MagicMock(return_value='connection succeeded')
        result = self.amity.save_state(database_name)

        print("Connection succeed: ", result)
        sqlite3.connect.assert_called_with(self.amity.database_directory + database_name)
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

    def test_load_state_gives_informative_message_when_database_is_empty(self):

        database_name = self.amity.empty_db
        sqlite3.connect = MagicMock(return_value="No data to Load. Empty database '%s'" % database_name)
        self.amity.load_state("databases/" + database_name)

        self.assertEqual(self.amity.connection, "No data to Load. Empty database '%s'" % database_name)

    def test_load_state_gives_informative_message_when_database_does_not_exist(self):
        database_name = "test_load_state_not_exist"
        sqlite3.connect = MagicMock(return_value=self.amity.error_codes[18] + " '%s'" % database_name)
        result = self.amity.load_state(database_name)
        self.assertEqual(result, self.amity.error_codes[18] + " '%s'" % database_name)

    def test_load_state_sqlite3_connect_fail_on_invalid_characters(self):
        sqlite3.connect = MagicMock(return_value='connection failed')
        result = self.amity.load_state('test_database/')
        self.assertEqual(result, self.amity.error_codes[17] + " 'test_database/'")
        result = self.amity.load_state('test_database*')
        self.assertEqual(result, self.amity.error_codes[17] + " 'test_database*'")

if __name__ == '__main__':
    unittest.main()
