import discord
from discord.ext import commands

from helpers.yaml_helper import read_yaml
from helpers.converters import ConvertToId


class RoadmapCog(commands.Cog, name='Roadmap Command', command_attrs=dict(pass_context=True)):
    def __init__(self, client):
        self.client = client

    @commands.group(brief='Get info on the current roadmap.')
    async def roadmap(self, ctx):
        """
        Gets updates from the SC Roadmap https://robertsspaceindustries.com/roadmap/board/1-Star-Citizen

        Commands:
        !roadmap patch [patch number] - gets patch details
        !roadmap category ["name"] - Gets a feature category. Surround with quotes for spaces
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Roadmap commands are !roadmap patch [patch] and !roadmap category "category name"')

    @roadmap.command(brief='Gets patch info')
    async def patch(self, ctx, patch: str):
        """
            Gets details of a patch and it's categories. !roadmap category can be used for each category

            patch - Patch number.
        """
        yaml_data = read_yaml('patches-parsed-09-16-2019')
        patch_data = next((item for item in yaml_data if item['patch'] == patch), None)

        embed = discord.Embed()
        for category in patch_data['categories']:
            if category['status'] == 'Polishing':
                embed_value = f"```{category['status']}```"
            else:
                embed_value = f"```{category['status']} - {category['progress']}```"

            embed.add_field(
                name=category['name'],
                value=embed_value,
                inline=False
            )

        await ctx.send(f"Patch: {patch_data['patch']}, Release Quarter: {patch_data['release_quarter']}", embed=embed)

    @roadmap.command(brief='Gets a roadmap category')
    async def category(self, ctx, category: ConvertToId()):
        """
            Gets a feature category. Surround with quotes for spaces

            "name" - Category Name. Surround with quotes for spaces
        """

        yaml_data = read_yaml('patches-parsed-09-16-2019')
        category_dict = {}
        patch_name = None

        for patch in yaml_data:
            for section in patch['categories']:
                if section['id'] == category:
                    category_dict = section
                    patch_name = patch['patch']
                    break

        if not category_dict:
            await ctx.send('No category by that name')
            return

        embed = {
            'thumbnail': {
                'url': category_dict['thumbnail']
            },
            'title': category_dict['name'],
            'description': f"Patch: {patch_name} \n \n {category_dict['description']}",
            'fields': [
                {
                    'name': 'Task Status',
                    'value': category_dict['status'],
                    'inline': True
                }
            ]
        }

        if category_dict['status'] == 'In Progress':
            embed['fields'].append({
                'name': 'Progress',
                'value': f"{category_dict['progress']}",
                'inline': True
            })

            embed['color'] = 16742152

        else:
            embed['color'] = 65314

        await ctx.send(embed=discord.Embed().from_dict(embed))


def setup(client):
    client.add_cog(RoadmapCog(client))
