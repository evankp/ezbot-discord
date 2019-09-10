import discord
from discord.ext import commands
import datetime
import pytz

from helpers.yaml_helper import read_yaml
from helpers.command_args import Arguments
import cron_job

TOKEN = read_yaml('tokens')['bot_token']
client = commands.Bot(command_prefix="!", pm_help=True)

available_timezones = {
    'PST': 'America/Los_Angeles',
    'PDT': 'America/Los_Angeles',
    'CST': 'America/Chicago',
    'EST': 'America/New_York',
    'JST': 'Asia/Tokyo'
}


def to_24_time(date):
    twelve_hour_time = datetime.datetime.strptime(date, '%m/%d/%Y %I:%M %p').strftime('%m/%d/%Y %H:%M')
    return datetime.datetime.strptime(twelve_hour_time, '%m/%d/%Y %H:%M')


def to_utc(timezone, date):
    return timezone.normalize(timezone.localize(date)).astimezone(pytz.utc)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        print(f'{message.author.name} said: {message.content}')
    await client.process_commands(message)


@client.command(pass_context=True, brief='Set an event')
async def set_event(ctx, *args):
    arguments = Arguments(
        date=('datetime', '%m/%d/%Y'),
        time=('datetime', '%I:%M'),
        period=('datetime', '%p'),
        timezone=('string', '^[A-Z]{3}$')
    )

    parsed_args = arguments.parse(keys=['date', 'time', 'period', 'timezone'], values=args)

    if parsed_args['timezone'] not in available_timezones:
        await ctx.channel.send(f'Timezones supported: '
                               f'{[key for key, value in available_timezones.items()]}.'
                               f' Please contact @Ezoss with the name of the timezone from '
                               f'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List'
                               f' for timezone to be added')
        return

    timezone = pytz.timezone(available_timezones[parsed_args['timezone']])
    requested_date = f"{parsed_args['date']} {parsed_args['time']} {parsed_args['period']}"

    try:
        date = to_utc(timezone, to_24_time(requested_date))
        cron_statement = f'cron({date.minute} {date.hour} {date.day} {date.month} ? {date.year})'
        cron_job.create_event(
            user=ctx.message.author.name,
            cron_expression=cron_statement,
            event='test',
            description='Testing description'
        )
    except ValueError:
        await ctx.channel.send('Not a valid date')


@client.command(pass_context=True, brief='Deletes messages')
@commands.has_any_role('Owner', 'Admin')
async def clear(ctx, num=10):
    number = int(num)
    async for message in ctx.channel.history(limit=number):
        await message.delete()

    print('Done!')

client.run(TOKEN)
