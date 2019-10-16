import boto3
import yaml
import requests
from datetime import timedelta, datetime

import helpers.sc_roadmap as roadmap
from helpers.time import last_update_date

s3 = boto3.resource('s3', region_name='us-west-2')
events = boto3.client('events', region_name='us-west-2')

bucket = 'evankp-discord-bot'


def parser(event, context):
    # Check if roadmap is updated
    rule_name = 'recheck-roadmap-api'
    response = requests.get('https://robertsspaceindustries.com/api/roadmap/v1/boards/1').json()
    response_date = datetime.fromtimestamp(response['data']['last_updated']).day
    try:
        # Function first executed every Friday at 20 o'clock at UTC time (1:30 PM PDT);
        # Cancel cron job after x hours past.
        if not event.get('test'):
            if rule_name in event['resources'][0] and datetime.utcnow().hour >= 24:
                events.disable_rule(Name=rule_name)
                print('Roadmap not updated and rule disabled.')

        # Enable a rule that will trigger function again, to check if roadmap has been updated.
        if response_date != datetime.utcnow().day:
            events.enable_rule(Name=rule_name)
            print('Roadmap not updated')
            return

        #  If roadmap has been updated, disable the rule that checks every hour
        if events.describe_rule(Name=rule_name)['State'] == 'ENABLED':
            events.disable_rule(Name=rule_name)
    except events.exceptions.ResourceNotFoundException:
        print(f'The rule ({rule_name}) does not exist')

    # Create and sve new data
    file_name = f"patch-data/patches-parsed-{last_update_date()}.yaml"
    new_data = roadmap.get_releases_parsed()

    if event.get('test'):
        file_name = f"patch-data/test/patches-parsed-{last_update_date()}.yaml"

    s3.Object(bucket, file_name).put(
        Body=bytes(yaml.dump(new_data, encoding=('utf-8')))
    )

    # Load previous week's data
    file_name = f"patch-data/patches-parsed-" \
                f"{(last_update_date(datetime_obj=True) - timedelta(weeks=1)).strftime('%m-%d-%Y')}.yaml"
    old_data = yaml.safe_load(s3.Object(bucket, file_name).get()['Body'])

    # Parse data
    differences = roadmap.compare_patch_differences(old_data=old_data, new_data=new_data)

    # Save differences data
    file_name = f"patch-data/roadmap-update-{last_update_date()}.yaml"
    if event.get('test'):
        file_name = f"patch-data/test/roadmap-update-{last_update_date()}.yaml"

    s3.Object(bucket, file_name).put(
        Body=bytes(yaml.safe_dump(differences, encoding=('utf-8')))
    )

    print('Parse Success')
