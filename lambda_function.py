import requests
import boto3
import pytz
from datetime import datetime

from helpers.yaml_helper import read_yaml
from helpers.database import get_event
from helpers.time import to_timezone

TOKEN = read_yaml('tokens')['bot_token']

client = boto3.client('events')


def send_discord_message(event, context):
    channel = read_yaml('tokens')['test_channel']
    db_event = get_event(event['rule'])

    date = to_timezone(pytz.utc, db_event['date'], db_event['timezone']).strftime('%m/%d/%Y')

    response = requests.post(f'https://discordapp.com/api/channels/{channel}/messages',
                             headers={'Authorization': f'Bot {TOKEN}', 'Content-Type': 'application/json'},
                             json={
                                 'tts': False,
                                 'embed': {
                                    'title': db_event['title'],
                                    'thumbnail': {
                                        'url': 'https://www.pngfind.com/pngs/m/218-2188123_3-star-citizen-logo-png-transparent-png.png'
                                    },
                                    'fields': [
                                        {
                                            'name': 'Organizer',
                                            'value': db_event['user'],
                                            'inline': True
                                        },
                                        {
                                            'name': 'Date/Time',
                                            'value': f"{date} {db_event['time']} \n {db_event['timezone']}",
                                            'inline': True
                                        },
                                        {
                                            'name': 'Description',
                                            'value': db_event['description']
                                        }
                                    ]
                                 }
                             }).json()

    client.remove_targets(
        Rule=event['rule'],
        Ids=[event['target_id']]
    )

    client.delete_rule(
        Name=event['rule']
    )

    return response
