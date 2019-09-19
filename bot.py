import discord
from discord.ext import commands
import typing

from helpers.yaml_helper import read_yaml
from helpers.converters import IncorrectValue, DateTimeConverter, TimeZoneConverter
import helpers.time as time_helper
import cron_job
from usc_ships import get_user_ships

TOKEN = read_yaml('tokens')['bot_token']
client = commands.Bot(command_prefix="!", help_command=commands.DefaultHelpCommand(dm_help=True))

COGS = [
    'cogs.events',
    'cogs.roadmap',
    'cogs.ships'
]

#####
# EVENT DEFINITIONS
#####


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.event
async def on_message(message):
    # if message.author.id != client.user.id:
    #     print(f'{message.author.name} said: {message.content}')

    if message.content.startswith('!help'):
        await message.channel.send("DM'ing you help info")

    await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    ignore_global_action = ['event set']

    if f'{ctx.command.parent.name} {ctx.command.name}' not in ignore_global_action:
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
    if ctx.message.channel.type != 'text':
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    await client.logout()
    await client.close()


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

if __name__ == '__main__':
    for cog in COGS:
        client.load_extension(cog)

    client.run(TOKEN)
