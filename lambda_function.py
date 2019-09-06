import requests

from helpers.yaml_helper import read_yaml

TOKEN = read_yaml('tokens')['bot_token']


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
                             })

    return response.json()
