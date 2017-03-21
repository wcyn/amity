import random

from .room import Office, LivingSpace


class Person(object):
    def __init__(self, first_name, last_name, **kwargs):
        # If not defined, id is None
        self.person_id = kwargs.pop('id', random.randrange(0, 99999))
        # If not defined, allocated_office_space is None
        self.allocated_office_space = kwargs.pop('allocated_office_space',
                                                 None)
        self.first_name = first_name
        self.last_name = last_name

    # Override the __new__() method
    def __new__(cls, *args, **kwargs):
        if cls is Person:
            raise TypeError("The Person class may not be instantiated")
        return super(Person, cls).__new__(cls)

    @property
    def person_id(self):
        """

        :return:
        :rtype:
        """
        return int(self.__id)

    @person_id.setter
    def person_id(self, person_id):
        self.__person_id = int(person_id)

    @property
    def first_name(self):
        """

        :return:
        :rtype:
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        if first_name.islower() or first_name.istitle():
            self.__first_name = ''.join(first_name.split()).title()
        else:
            self.__first_name = ''.join(first_name.split())

    @property
    def last_name(self):
        """

        :return:
        :rtype:
        """
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        if last_name.islower() or last_name.istitle():
            self.__last_name = ''.join(last_name.split()).title()
        else:
            self.__last_name = ''.join(last_name.split())

    @property
    def allocated_office_space(self):
        """

        :return:
        :rtype:
        """
        return self.__allocated_office_space

    @allocated_office_space.setter
    def allocated_office_space(self, office_space):
        if isinstance(office_space, Office):
            # If Person already had an Office Space, decrement number of
            # occupants from previous office space
            if isinstance(self.__allocated_office_space, Office):
                self.__allocated_office_space.num_of_occupants -= 1
            # Automatically increment number of occupants in newly allocated
            #   office
            office_space.num_of_occupants += 1
            self.__allocated_office_space = office_space
        elif office_space:
            # Office space is not None
            # Cannot assign Non-Office instance to allocated_office_space
            print("Cannot assign non-offices instance to  "
                  "allocated_office_space")
            self.__allocated_office_space = None
        else:
            self.__allocated_office_space = None


class Staff(Person):

    def __init__(self, *args, **kwargs):
        super(Staff, self).__init__(*args, **kwargs)


class Fellow(Person):

    def __init__(self, *args, **kwargs):
        super(Fellow, self).__init__(*args, **kwargs)
        # Default is None
        self.allocated_living_space = kwargs.pop(
                'allocated_living_space', None)
        # Default is False, meaning No
        self.wants_accommodation = kwargs.pop(
                'wants_accommodation', False)

    @property
    def allocated_living_space(self):
        """

        :return:
        :rtype:
        """
        return self.__allocated_living_space

    @property
    def allocated_office_space(self):
        """

        :return:
        :rtype:
        """

    @allocated_living_space.setter
    def allocated_living_space(self, living_space):
        """

        :param living_space:
        :type living_space:
        :return:
        :rtype:
        """
        if isinstance(living_space, LivingSpace):
            # If Fellow already had a Living Space, decrement number of
            # occupants from previous living space
            if isinstance(self.__allocated_living_space, LivingSpace):
                self.__allocated_living_space.num_of_occupants -= 1
            # Automatically increment number of occupants in newly allocated
            #   living space
            living_space.num_of_occupants += 1
            self.__allocated_living_space = living_space
        elif living_space:
            # Living space is not None
            # Cannot assign Non-LivingSpace instance to allocated_living_space
            print("Cannot assign Non-LivingSpace instance to  "
                  "allocated_living_space")
            self.__allocated_living_space = None
        else:
            self.__allocated_living_space = None

    @property
    def wants_accommodation(self):
        """

        :return:
        :rtype:
        """
        return self.__wants_accommodation

    @wants_accommodation.setter
    def wants_accommodation(self, wants_accommodation):
        if wants_accommodation:
            self.__wants_accommodation = True
        else:
            self.__wants_accommodation = False
