import discord
from discord.ext import commands

from helpers.converters import IncorrectValue, DateTimeConverter, TimeZoneConverter
import helpers.time as time_helper
from helpers.cog_funcs import *

import cron_job


class EventsCog(commands.Cog, name='Event Command', command_attrs=dict(pass_context=True)):
    def __init__(self, client):
        self.client = client

    @commands.group(brief='Event reminders and useful functions.')
    async def event(self, ctx):
        """
            Various functions for event reminders

            !event set - Set an event
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(cog_help(ctx))

    @event.command(brief='Set an event')
    async def set(self, ctx,
                  date: DateTimeConverter(compare_string='%m/%d/%Y', correct_format='MM/DD/YYYY'),
                  time: DateTimeConverter(compare_string='%I:%M', correct_format='HH:MM (12 hour format)'),
                  period: DateTimeConverter(compare_string='%p', correct_format='AM/PM'),
                  timezone: TimeZoneConverter(),
                  title: str,
                  description: str
                  ):
        """
            Set an event reminder that will be triggered at the specified time. Uses AWS CloudWatch Events

            Parameters:
            <date> - String in form of MM?/DD/YYYY
            <time> - String in form of HH:MM in 12 hour format
            <period> - String in form of AM/PM for 12 hour format
            <timezone>: Timezone abbrevation, limited to:
                'PST': 'America/Los_Angeles',
                'PDT': 'America/Los_Angeles',
                'CST': 'America/Chicago',
                'EST': 'America/New_York',
                'JST': 'Asia/Tokyo'
            <title> - Title of the event, used in the reminder title
            <description> - Description of the event, used in the reminder body
             None
        """

        try:
            date_object = time_helper.to_utc(timezone, time_helper.to_24_time(f"{date} {time} {period}"))
            cron_statement = f'cron({date_object.minute - 1} {date_object.hour} {date_object.day} {date_object.month} ? {date_object.year})'
            cron_job.create_event(
                user=ctx.message.author.name,
                cron_expression=cron_statement,
                event=title,
                description=description,
                time_info={
                    'date': date_object.timestamp(),
                    'time': f'{time} {period}',
                    'timezone': str(timezone)
                }
            )
        except ValueError as error:
            await ctx.channel.send(error)

    # @set.error
    # async def set_error(self, ctx, error):
    #     if isinstance(error, IncorrectValue):
    #         await ctx.send(error)
    #     elif isinstance(error, commands.ConversionError):
    #         print(error)
    #     else:
    #         print(error)
    #         await ctx.send('Correct command format is !set_event [MM/DD/YYYY] [HH:MM] [AM/PM] [TIMEZONE] '
    #                        '["title"] ["description"]')


def setup(client):
    client.add_cog(EventsCog(client))
