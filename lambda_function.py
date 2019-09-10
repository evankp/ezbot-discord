import requests
import boto3

from helpers.yaml_helper import read_yaml

TOKEN = read_yaml('tokens')['bot_token']

client = boto3.client('events')


def send_discord_message(event, context):
    channel = read_yaml('tokens')['test_channel']
    response = requests.post(f'https://discordapp.com/api/channels/{channel}/messages',
                             headers={'Authorization': f'Bot {TOKEN}', 'Content-Type': 'application/json'},
                             json={
                                 'tts': False,
                                 'embed': {
                                    'title': event['title'],
                                    'description': event['description']
                                 }
                             }).json()

    if 'code' not in response:
        client.remove_targets(
            Rule=event['rule'],
            Ids=[event['target_id']]
        )

        client.delete_rule(
            Name=event['rule']
        )

    return response
