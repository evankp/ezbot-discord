import discord
from discord.ext import commands

from helpers.yaml_helper import read_yaml
from helpers.command_args import IncorrectValue, DateTimeConverter, TimeZoneConverter
import helpers.time as time_helper
import cron_job

TOKEN = read_yaml('tokens')['bot_token']
client = commands.Bot(command_prefix="!", pm_help=True)

#####
# EVENT DEFINITIONS
#####


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        print(f'{message.author.name} said: {message.content}')
    await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    ignore_global_action = ['set_event']

    if ctx.invoked_with not in ignore_global_action:
        await ctx.send(error)

#####
# COMMAND DEFINITIONS
#####


@client.command(hidden=True)
@commands.is_owner()
async def kill(ctx):
    """
        Kills the Bot from Discord, must be the owner
    """
    async for message in ctx.channel.history(limit=1):
        await message.delete()

    await client.logout()
    await client.close()


@client.command(pass_context=True, brief='Set an event')
async def set_event(ctx,
                    date: DateTimeConverter(compare_string='%m/%d/%Y', correct_format='MM/DD/YYYY'),
                    time: DateTimeConverter(compare_string='%I:%M', correct_format='HH:MM (12 hour format)'),
                    period: DateTimeConverter(compare_string='%p', correct_format='AM/PM'),
                    timezone: TimeZoneConverter(),
                    title: str,
                    description: str
                    ):
    """
        Discord Chat bot command
        Set an event reminder that will be triggered at the specified time. Uses AWS CloudWatch Events
        :param ctx: discord.py context object
        :param date: String in form of MM?/DD/YYYY
        :param time: String in form of HH:MM in 12 hour format
        :param period: String in form of AM/PM for 12 hour format
        :param timezone: Timezone abbrevation, limited to:
            'PST': 'America/Los_Angeles',
            'PDT': 'America/Los_Angeles',
            'CST': 'America/Chicago',
            'EST': 'America/New_York',
            'JST': 'Asia/Tokyo'
        :param title: Title of the event, used in the reminder title
        :param description: Description of the event, used in the reminder body
        :return None
    """

    try:
        date_object = time_helper.to_utc(timezone, time_helper.to_24_time(f"{date} {time} {period}"))
        cron_statement = f'cron({date_object.minute} {date_object.hour} {date_object.day} {date_object.month} ? {date_object.year})'
        cron_job.create_event(
            user=ctx.message.author.name,
            cron_expression=cron_statement,
            event=title,
            description=description,
            time_info={
                'date': date,
                'time': f'{time} {period}',
                'timezone': str(timezone)
            }
        )
    except ValueError as error:
        await ctx.channel.send(error)


@set_event.error
async def set_event_error(ctx, error):
    if isinstance(error, IncorrectValue):
        await ctx.send(error)
    elif isinstance(error, commands.ConversionError):
        print(error)
    else:
        print(error)
        await ctx.send('Correct command format is !set_event [MM/DD/YYYY] [HH:MM] [AM/PM] [TIMEZONE] '
                       '["title"] ["description"]')


@client.command(pass_context=True, brief='Deletes messages')
@commands.has_any_role('Owner', 'Admin')
async def clear(ctx, num=10):
    """
    Discord chat bot command to clear X messages, including the command message
    :param ctx: Discord.py context object
    :param num: Number of messages to clear
    :return None
    """

    number = int(num)
    number += 1

    async for message in ctx.channel.history(limit=number):
        await message.delete()

    print('Done!')

client.run(TOKEN)
