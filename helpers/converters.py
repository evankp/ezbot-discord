import datetime
import re
import pytz
from discord.ext import commands


class IncorrectValue(commands.BadArgument):
    """ Raised when argument does not match specified value"""
    pass


class DateTimeConverter(commands.Converter):
    def __init__(self, *, compare_string, correct_format):
        self.compare_string = compare_string
        self.correct_format = correct_format

    async def convert(self, ctx, argument):
        try:
            datetime.datetime.strptime(argument, self.compare_string)
            return argument
        except ValueError:
            raise IncorrectValue(f'Value ({argument}) is not of correct date/time ({self.correct_format})')


class StringMatchConverter(commands.Converter):
    def __init__(self, *, pattern=None, correct_format=None):
        self.pattern = pattern
        self.correct_format = correct_format

    async def convert(self, ctx, argument):
        if self.pattern is not None and re.match(self.pattern, argument) is None:
            raise IncorrectValue(f'{argument} must match "{self.correct_format}"')

        return argument


class TimeZoneConverter(commands.Converter):
    def __init__(self):
        self.available_timezones = {
            'PST': 'America/Los_Angeles',
            'PDT': 'America/Los_Angeles',
            'CST': 'America/Chicago',
            'EST': 'America/New_York',
            'JST': 'Asia/Tokyo'
        }

    async def convert(self, ctx, argument):
        if re.match('^[A-Z]{3}$', argument) is None:
            raise IncorrectValue(f'Value: {argument} does not match timezone abbreviation (EX: PST)')

        if argument not in self.available_timezones:
            raise IncorrectValue(f'Timezones supported: '
                                 f'{[key for key, value in self.available_timezones.items()]}.'
                                 f' Please contact @Ezoss with the name of the timezone from '
                                 f'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List'
                                 f' for timezone to be added')

        return pytz.timezone(self.available_timezones[argument])


class ConvertToId(commands.Converter):
    async def convert(self, ctx, argument):
        return argument.replace(' ', '-').replace('(', '').replace(')', '').lower()


class Capitalize(commands.Converter):
    async def convert(self, ctx, argument):
        arg = " ".join(w.capitalize() for w in str(argument).split())
        return arg
