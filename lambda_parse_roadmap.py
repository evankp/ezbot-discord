import boto3
import yaml
from datetime import timedelta

import helpers.sc_roadmap as roadmap
from helpers.time import last_update_date

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = 'evankp-discord-bot'


def create_new_parsed_data(test: bool):
    new_data = roadmap.get_releases_parsed()
    file_name = f"patch-data/patches-parsed-{last_update_date()}.yaml"

    if test:
        file_name = f"patch-data/test/patches-parsed-{last_update_date()}.yaml"

    s3.Object(bucket, file_name).put(
        Body=bytes(yaml.dump(new_data, encoding=('utf-8')))
    )

    return new_data


def load_old_data():
    file_name = f"patch-data/patches-parsed-" \
        f"{(last_update_date(datetime_obj=True) - timedelta(weeks=1)).strftime('%m-%d-%Y')}.yaml"

    return yaml.safe_load(s3.Object(bucket, file_name).get()['Body'])


def save_differences(test: bool, data):
    file_name = f"patch-data/roadmap-update-{last_update_date()}.yaml"
    if test:
        file_name = f"patch-data/test/roadmap-update-{last_update_date()}.yaml"

    s3.Object(bucket, file_name).put(
        Body=bytes(yaml.safe_dump(data, encoding=('utf-8')))
    )


def parser(event, context):
    # Output files to test folder if a test
    test_parse = False
    if 'test' in event:
        test_parse = event['test']

    # Create new data
    new_data = create_new_parsed_data(test_parse)

    # Load previous week's data
    old_data = load_old_data()

    # Parse and save update data
    differences = roadmap.compare_patch_differences(old_data=old_data, new_data=new_data)
    save_differences(test_parse, differences)
