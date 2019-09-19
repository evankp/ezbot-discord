import discord
from discord.ext import commands
import typing

from usc_ships import get_user_ships


class ShipCog(commands.Cog):
    def __init__(self, cliet):
        self.client = cliet

    @commands.group()
    async def ships(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Ship commands are !ships get [Optional: user]')

    @ships.command(pass_context=True)
    async def get(self, ctx, user: typing.Optional[str]):
        if not user:
            user = ctx.message.author.name

        user_data = get_user_ships(user)

        await ctx.send("User '{0}' has {1} ships: ```\n{2}```".format(user_data['name'],
                                                                      user_data['number'],
                                                                      '\n'.join(user_data['ships'])))


def setup(client):
    client.add_cog(ShipCog(client))
