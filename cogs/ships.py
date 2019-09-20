import discord
from discord.ext import commands
import typing

from usc_ships import get_user_ships


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

        await ctx.send("User '{0}' has {1} ships: ```\n{2}```".format(user_data['name'],
                                                                      user_data['number'],
                                                                      '\n'.join(user_data['ships'])))


def setup(client):
    client.add_cog(ShipCog(client))
