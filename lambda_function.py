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
                                    'thumbnail': {
                                        'url': 'https://www.pngfind.com/pngs/m/218-2188123_3-star-citizen-logo-png-transparent-png.png'
                                    },
                                    'fields': [
                                        {
                                            'name': 'Organizer',
                                            'value': event['user'],
                                            'inline': True
                                        },
                                        {
                                            'name': 'Date/Time',
                                            'value': f"{event['time_info']['date']} "
                                            f"{event['time_info']['time']} \n {event['time_info']['timezone']}",
                                            'inline': True
                                        },
                                        {
                                            'name': 'Description',
                                            'value': event['description']
                                        }
                                    ]
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
