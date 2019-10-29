import boto3
import yaml
import discord
from discord import Webhook, RequestsWebhookAdapter

import helpers.yaml_helper as yaml_helper
from helpers.sc_roadmap import format_update_embed
from helpers.time import last_update_date


s3 = boto3.resource('s3', region_name='us-west-2')


def lambda_handler(event, context):
    webhooks = yaml_helper.read_yaml('webhooks')
    for webhook in webhooks:
        wh = Webhook.partial(webhook['webhook_id'], webhook['webhook_token'], adapter=RequestsWebhookAdapter())

        patch_data = yaml.safe_load(s3.Object('evankp-discord-bot',
                                              f'patch-data/patches-parsed-{last_update_date()}.yaml').get()['Body'])

        patch = patch_data[0]['patch']
        embed = format_update_embed(patch=patch, patch_data=patch_data)

        if not isinstance(embed, discord.Embed) and 'error' in embed:
            return embed['error']

        wh.send(f"{patch} Updates - {last_update_date(datetime_obj=True).strftime('%B %d, %Y')}",
                            username='Roadmap Updates',
                            embed=embed)
