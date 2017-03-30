[![Build Status](https://travis-ci.org/andela-wcyn/amity.svg?branch=develop)](https://travis-ci.org/andela-wcyn/amity) [![Coverage Status](https://coveralls.io/repos/github/andela-wcyn/amity/badge.svg?branch=develop)](https://coveralls.io/github/andela-wcyn/amity?branch=develop)
# Amity

A room Allocation system for Fellows and Staff.
This application manages Fellow and Staff allocations to Offices and Living Spaces.

Amity has rooms which can be offices or living spaces. An office can accommodate a maximum of 6 people.
A living space can accommodate a maximum of 4 people.

A person to be allocated could be a fellow or staff.
Staff cannot be allocated living spaces.
Fellows have a choice to choose a living space or not.

Offices and Living Spaces are randomly allocated to the Staff or Fellows


![alt text](https://s16.postimg.org/62q7weoz9/Screen_Shot_2017_03_16_at_6_31_42_AM.png "Amity Room Allocation Application")

### The following are the main functions:
`create_room <room_name>...`
- Creates a one or more rooms and adds them to Amity
- <room_name> The name of the room to be created or printed. Add '-ls' at the end of the room name to indicate that it is a living space. Default is office

`add_person <first_name> <last_name> <role> [<wants_accommodation>]`
- Adds a person to amity and allocates a random room to them
- `<first_name>`   The first name of the Fellow or Staff
- `<last_name>` The last name of the Fellow or Staff
- `<role>`  The role of the new person, either Fellow or Staff
- `<wants_accommodation>` Indication of if the Fellow wants accommodation or not. Choices ('N','No', 'Yes','Y')

`reallocate_person <person_identifier> <new_room_name>`
- It allocates a person from one room to another
- `<person_identifier>`       A Unique User identifier of the Fellow or Staff
- `<new_room_name>`       The Room name to which the Fellow or Staff is to be reallocated

`load_people <filename>`
- Loads people into Amity from a text file
- `<filename>` The filename to load data from

`print_allocations [-o=filename]`
- Prints a list of allocations onto the screen.
- Specifying the optional  -o  option outputs the registered allocations to a txt file.

`print_unallocated [-o=filename]`
- Prints a list of unallocated people to the screen
- Specifying the  -o  option outputs the information to the txt file provided.

`print_room <room_name>`
- Prints the names of all the people in  `room_name`  on the
screen

`save_state [--db=sqlite_database]`
- Persists all the data stored in the app to a SQLite database.
- Specifying the  --db  parameter explicitly stores the data in the sqlite_database  specified.

`load_state [<sqlite_database>]`
- Loads data from a database into the application


### How to run this program
First, ensure that all the requirements have been installed by running:
```$ pip install -r requirements.txt```

In order to run this file. Change directory into the root folder, and then run:
```
$ python app.py -i
```

### Tests:
About 111 tests have been added to the `tests/test_amity.py` file
These tests test the main functionality of Amity


### How to manually test Amity
First, change directory into the root folder.
```$ cd amity```
Finally, at the root of the project folder, execute the following command:
```$ nosetests --rednose --with-coverage --cover-package=models```

![alt text](http://oi64.tinypic.com/fbywkz.jpg "Amity Nose Tests")
