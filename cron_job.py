import boto3

events = boto3.client('events')
""" :type: pyboto3.events"""


def create_job(event_name):
    return events.put_rule(Name=event_name, ScheduleExpression='rate(1 minute)', State='DISABLED')


def put_target():
    return events.put_targets(Rule='test_event', Targets=[
        {
            'Id': '1',
            'Arn': 'arn:aws:lambda:us-west-1:758538057083:function:terminate-ec2-instance-timed'
         }
    ])


if __name__ == '__main__':
    create_job()
    # print(put_target())
