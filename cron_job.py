import boto3
import json
import helpers.database as db

from helpers.yaml_helper import read_yaml
from helpers.numerical import random_number

events = boto3.client('events')
""" :type: pyboto3.events"""

DISCORD_TOKEN = read_yaml('tokens')['bot_token']


def create_job(user: str, cron: str):
    rule_name = f'{user}-{random_number(5)}'

    rule_arn = events.put_rule(
        Name=rule_name,
        ScheduleExpression=cron,
        State='ENABLED'
    )['RuleArn']

    return {'arn': rule_arn, 'rule_name': rule_name}


def put_target(user: str, rule_name: str):
    target_id = f'{user}-{random_number(10)}'

    events.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': target_id,
                'Arn': read_yaml('tokens')['lambda_arn'],
                'Input': json.dumps({
                    'target_id': target_id,
                    'rule': rule_name
                })
             }
        ]
    )

    return target_id


def create_event(user: str, cron_expression: str, event: str, description: str, time_info: dict):
    job = create_job(user, cron_expression)

    db.add_event(job['rule_name'],
                 date=time_info['date'],
                 time=time_info['time'],
                 timezone=time_info['timezone'],
                 user=user,
                 title=event,
                 description=description)

    target_id = put_target(user, job['rule_name'])

    return {'job': job, 'target_id': target_id}
