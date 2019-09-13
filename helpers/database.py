import boto3
from pprint import pprint

db = boto3.client('dynamodb', region_name='us-west-2')
""" :type: pyboto3.dynamodb """

events_table = 'usc_events'

DB_TYPES = {
    'list': 'L',
    'int': 'N',
    'str': 'S'
}


def add_secondary_key(key: str, type: str):
    try:
        response = db.update_table(
            TableName=events_table,
            AttributeDefinitions=[
                {
                    'AttributeName': key,
                    'AttributeType': type
                }
            ],
            GlobalSecondaryIndexUpdates=[
                {
                    'Create': {
                        'IndexName': f'{key}_index',
                        'KeySchema': [{'AttributeName': key, 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
                    }
                }
            ]
        )

        return response
    except Exception as error:
        return error


def add_event(event_id, **kwargs):
    event = {'event_id': {'S': event_id}}

    for key, value in kwargs.items():
        if isinstance(value, str):
            event[key] = {'S': value}
        elif isinstance(value, int):
            event[key] = {'N': str(value)}
        elif isinstance(value, list):
            value = [str(item) for item in value]
            event[key] = {'L': value}
        elif isinstance(value, bool):
            event[key] = {'BOOL': value}

    return db.put_item(
        TableName=events_table,
        Item=event
    )


def get_event(id):
    resp = db.get_item(TableName=events_table, Key={'event_id': {'S': id}})['Item']

    return {key: value['S'] for key, value in resp.items()}


if __name__ == '__main__':
    pprint(get_event('Ezoss-29684'))
