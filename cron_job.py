import boto3

from helpers.yaml_helper import read_yaml

events = boto3.client('events')
""" :type: pyboto3.events"""

DISCORD_TOKEN = read_yaml('tokens')['bot_token']


def create_job(event_name):
    return events.put_rule(Name=event_name, ScheduleExpression='rate(1 minute)', State='DISABLED')


def put_target(event_name):
    return events.put_targets(Rule=event_name, Targets=[
        {
            'Id': '1',
            'Arn': read_yaml('tokens')['lambda_arn']
         }
    ])


if __name__ == '__main__':
    create_job()
    # print(put_target())
