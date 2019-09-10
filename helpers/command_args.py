import datetime
import re


class MismatchArgument(Exception):
    """ Raised when argument does not match specified value"""
    pass


class ArgumentDoesNotExist(Exception):
    """ Raised when an argument provided at parse was not defined when initializing argument object"""
    pass


class Arguments:
    def __init__(self, **kwargs):
        self.__argument_types = ['datetime', 'string']
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def __assign_arguments(arguments, array):
        return_args = {}
        for index, value in enumerate(arguments):
            return_args[value] = array[index]

        return return_args

    def parse(self, keys, values):
        assigned_arguments = Arguments.__assign_arguments(keys, values)
        parsed_values = {}

        for key, value in assigned_arguments.items():
            if not getattr(self, key):
                raise ArgumentDoesNotExist

            argument_attr = getattr(self, key)

            if argument_attr[0] == 'string':
                if re.match(argument_attr[1], value) is None:
                    raise MismatchArgument(f'{argument_attr[1]}')
            elif argument_attr[0] == 'datetime':
                try:
                    datetime.datetime.strptime(value, argument_attr[1])
                except ValueError:
                    raise MismatchArgument(f'Value ({value}) is not of correct time ({argument_attr[1]})')
            else:
                argument_attr[0](argument_attr[1], value)

            parsed_values[key] = value

        return parsed_values
