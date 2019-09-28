import discord
from discord.ext import commands

from datetime import datetime
from helpers.converters import ConvertToId
import helpers.sc_roadmap as roadmap_helper
import helpers.yaml_helper as yaml_helper
from helpers.time import last_update_date
from helpers.cog_funcs import *


# For the roadmap commands to work, the get_releases_parsed function needs to be run in helpers/sc-roadmap.py,
# the updates command needs to have two weeks worth of data, but will just respond with not enough data
class RoadmapCog(commands.Cog, name='Roadmap Command', command_attrs=dict(pass_context=True)):
    def __init__(self, client):
        self.client = client

    @commands.group(brief='Get info on the current roadmap.')
    async def roadmap(self, ctx):
        """
        Gets updates from the SC Roadmap https://robertsspaceindustries.com/roadmap/board/1-Star-Citizen
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(cog_help(ctx))

    @roadmap.command(brief='Gets patch info')
    async def patch(self, ctx, patch: str):
        """
            Gets details of a patch and it's feature. !roadmap feature can be used for each feature

            patch - Patch number.
        """
        roadmap_helper.download_patch_data_s3()
        data = yaml_helper.read_yaml(f'patch-data/patches-parsed-{last_update_date()}')
        patch_data = next((item for item in data if item['patch'] == patch), None)

        embed = discord.Embed()
        for feature in patch_data['features']:
            if feature['status'] == 'Polishing':
                embed_value = f"```{feature['status']}```"
            else:
                embed_value = f"```{feature['status']} - {feature['progress']}```"

            embed.add_field(
                name=feature['name'],
                value=embed_value,
                inline=False
            )

        await ctx.send(f"Patch: {patch_data['patch']}, Release Quarter: {patch_data['release_quarter']}", embed=embed)

    @roadmap.command(brief='Gets patch updates')
    async def updates(self, ctx, patch: str):
        """
        Get updates to patch since last roadmap update

        patch - patch number
        """
        roadmap_helper.download_patch_data_s3()
        data = roadmap_helper.get_latest_patch_updates(patch)
        if 'error' in data:
            await ctx.send(data['error'])
            return

        update_date = datetime.fromtimestamp(data['date']).strftime('%B %d, %Y')
        new_patch_data = next((item for item in yaml_helper.read_yaml(f'patch-data/patches-parsed-{last_update_date()}')
                               if item['patch'] == patch))

        embed = discord.Embed()

        for key, value in data['updates'].items():
            update = 'None'
            if value:
                update = ''
                if key == 'added':
                    for feature in value:
                        feature_data = next((item for item in new_patch_data['features'] if item['id'] == feature))

                        update += f"{feature_data['name']} \n ```{feature_data['description']}``` \n \n"

                elif key == 'removed':
                    # TODO: Need to update update method to account for features being removed/moved better
                    # Placeholder
                    update = value

                elif key == 'updated':
                    for feature_update in value:
                        feature_data = next((item for item in new_patch_data['features']
                                              if item['id'] == feature_update['feature']))

                        update += f"__{feature_data['name']}__\n\n"

                        for attribute_update in feature_update['attribute_updates']:
                            update += f"{attribute_update['attribute'].capitalize()}\n"
                            if not attribute_update['old']:
                                update += f"``` None -> {attribute_update['new']}```\n"
                            else:
                                update += f"``` {attribute_update['old']} -> {attribute_update['new']}```\n"
                else:
                    update = value

            embed.add_field(name=key.capitalize(), value=update, inline=False)

        await ctx.send(f'{patch} Updates - {update_date}', embed=embed)

    @roadmap.command(brief='Gets a roadmap feature')
    async def feature(self, ctx, feature: ConvertToId()):
        """
            Gets a feature. Surround with quotes for spaces

            "name" - Feature Name. Surround with quotes for spaces
        """
        roadmap_helper.download_patch_data_s3()
        data = yaml_helper.read_yaml(f'patch-data/patches-parsed-{last_update_date()}')
        feature_dict = {}
        patch_name = None

        for patch in data:
            for section in patch['features']:
                if section['id'] == feature:
                    feature_dict = section
                    patch_name = patch['patch']
                    break

        if not feature_dict:
            await ctx.send('No feature by that name')
            return

        embed = {
            'thumbnail': {
                'url': feature_dict['thumbnail']
            },
            'title': feature_dict['name'],
            'description': f"Patch: {patch_name} \n \n {feature_dict['description']}",
            'fields': [
                {
                    'name': 'Task Status',
                    'value': feature_dict['status'],
                    'inline': True
                }
            ]
        }

        if feature_dict['status'] == 'In Progress':
            embed['fields'].append({
                'name': 'Progress',
                'value': f"{feature_dict['progress']}",
                'inline': True
            })

            embed['color'] = 16742152

        else:
            embed['color'] = 65314

        await ctx.send(embed=discord.Embed().from_dict(embed))


def setup(client):
    client.add_cog(RoadmapCog(client))
