from discord.ext import commands

from helpers.yaml_helper import read_yaml

TOKEN = read_yaml('tokens')['bot_token']
client = commands.Bot(command_prefix="!")

COGS = [
    # 'cogs.events',
    'cogs.roadmap',
    'cogs.ships'
]


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')


@client.event
async def on_message(message):
    # if message.author.id != client.user.id:
    #     print(f'{message.author.name} said: {message.content}')

    await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Command "{ctx.message.content.split(" ")[0].replace("!", "")}" not found')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Missing the required "{str(error).split(" ")[0]}" parameter')
    else:
        await ctx.send('An unknown/code error happened!')
        print(error)
    # ignore_global_action = ['event set']
    # command_name = ''
    #
    # if hasattr(ctx.command, 'parent'):
    #     command_name = ctx.command.parent.name
    #
    # command_name += f' {ctx.command.name}'
    #
    # print(command_name)
    #
    # if command_name not in ignore_global_action:
    #     await ctx.send(error)


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
async def clear(ctx, num: int = 10, *args):
    """
    Discord chat bot command to clear X messages, including the command message
    :param ctx: Discord.py context object
    :param num: Number of messages to clear
    :return None
    """

    number = num
    number += 1

    async for message in ctx.channel.history(limit=number):
        await message.delete()

    if '-q' not in args:
        await ctx.channel.send(f'```{num} Messages Deleted```')


if __name__ == '__main__':
    for cog in COGS:
        client.load_extension(cog)

client.run(TOKEN)
