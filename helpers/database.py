import boto3
from pprint import pprint

db = boto3.client('dynamodb', region_name='us-west-2')
""" :type: pyboto3.dynamodb """

events_table = 'usc_events'
ship_table = 'usc_ships'


class Table:
    db_types = {
        'L': list,
        'N': int,
        'S': str,
        'SS': list
    }

    def __init__(self, name, primary_key):
        self.name = name
        self.primary_key = primary_key

    @classmethod
    def transform_to_python(cls, items):
        new_items = {}

        for key, value in items.items():
            item_type = list(value.keys())[0]
            item_value = list(value.values())[0]

            try:
                if item_type == 'L':
                    item = []

                    for sub_item in cls.db_types[item_type](item_value):
                        item.append(list(sub_item.values())[0])

                    new_items[key] = item
                    continue

                new_items[key] = cls.db_types[item_type](item_value)
            except KeyError:
                raise KeyError('Key type not in pre-determined types')

        return new_items

    def transform_to_database(self, key, **items):
        item = {self.primary_key: {'S': key}}

        for item_key, value in items.items():
            if isinstance(value, str):
                item[item_key] = {'S': value}
            elif isinstance(value, int) or isinstance(value, float):
                item[item_key] = {'N': str(value)}
            elif isinstance(value, list):
                value = [{'S': str(item)} for item in value]
                item[item_key] = {'L': value}
            elif isinstance(value, bool):
                item[item_key] = {'BOOL': value}

        return item

    def add_secondary_key(self, key: str, type: str):
        try:
            response = db.update_table(
                TableName=self.name,
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

    def set_item(self, key, **items):
        item = self.transform_to_database(key, **items)

        return db.put_item(
            TableName=self.name,
            Item=item
        )

    def get_item(self, key):
        resp = db.get_item(TableName=self.name, Key={self.primary_key: {'S': key}})['Item']

        return Table.transform_to_python(resp)

    def update_item(self, key, **update_items):
        update_key = self.transform_to_database(key, user=key)
        update_item = self.transform_to_database(key, **update_items)
        index = 0
        update_expression = 'SET '

        for key, value in update_items.items():
            update_expression += f"{key} = :{index}, "
            index += 1

        update_expression = update_expression.rstrip(', ')

        update_values = {f':{index - 1}': item[1] for index, item in enumerate(update_item.items())
                         if item[0] != 'user'}

        return db.update_item(
            TableName=self.name,
            Key=update_key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=update_values
        )


if __name__ == '__main__':
    ships = Table(ship_table, 'user')

    # pprint(ships.get_item('Landscaper'))
    # pprint(ships.get_item('Ezoss'))
    # pprint(ships.set_item('Ezoss', ships=['Kraken', '300i', '100i'], number=3))
    # ships.update_item('Ezoss', ship_number=3, ships=['Kraken', '300i', '100i'])
    pass
