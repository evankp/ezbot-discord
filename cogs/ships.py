import discord
from discord.ext import commands
import typing

from helpers.ships import get_user_ships, add_ships, remove_ships
from helpers.converters import Capitalize


class ShipCog(commands.Cog, name='Ship Command', command_attrs=dict(pass_context=True)):
    def __init__(self, client):
        self.client = client

    @commands.group(brief='USC ship functions - Get/set your fleet and ships')
    async def ships(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Ship commands are !ships get [Optional: user]')

    @ships.command()
    async def get(self, ctx, user: typing.Optional[typing.Union[discord.Member, str]]):
        if not user:
            user = ctx.message.author

        if isinstance(user, str):
            user_data = get_user_ships(user)
        else:
            user_data = get_user_ships(user.name)

        await ctx.send("User '{0}' has {1} ships: ```\n{2}```".format(user_data['user'],
                                                                      user_data['ship_number'],
                                                                      '\n'.join(user_data['ships'])))

    @ships.command()
    async def add(self, ctx, *ships: Capitalize):
        results = add_ships(ctx.author.name, *ships)

        if results['unsuccessful']:
            unsuccessful = ', '.join(results['unsuccessful'])
            await ctx.send(f'Ships "{unsuccessful}" not in ship list.')

        if results['added']:
            added = ', '.join(results['added'])
            await ctx.send(f'Added ships "{added}".')

    @ships.command()
    async def remove(self, ctx, *ships: Capitalize):
        results = remove_ships(ctx.author.name, *ships)

        if results['unsuccessful']:
            unsuccessful = ', '.join(results['unsuccessful'])
            await ctx.send(f'Ships "{unsuccessful}" not in your existing ship list.')

        if results['removed']:
            removed = ', '.join(results['removed'])
            await ctx.send(f'Removed ships "{removed}".')


def setup(client):
    client.add_cog(ShipCog(client))
