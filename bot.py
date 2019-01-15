import discord
from helpers.yaml_helper import read_yaml
from discord.ext import commands

import os

TOKEN = read_yaml('tokens')['discord_token']
OWNER = 257106225777475585
client = commands.Bot(command_prefix="!", pm_help=True)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        print(f'{message.author.name} said: {message.content}')
    await client.process_commands(message)


@client.command(pass_context=True, brief='DMs the owner of this bot.')
async def tell_owner(ctx, *args):
    owner_user = await client.get_user_info(OWNER)

    await owner_user.send(f'{ctx.author.mention} says "{args[0]}"')


@client.command(pass_context=True, brief='DMs a user -- message goes in quotes')
async def message(ctx, *args):
    user_to_message = int(args[0].replace('<@', '').replace('>', ''))
    dm_user = await client.get_user_info(user_to_message)

    await dm_user.send(f"{ctx.author.mention} wants to let you know '{args[1]}'")
    await ctx.send('Message sent!')

client.run(TOKEN)
