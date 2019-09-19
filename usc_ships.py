import csv
from pprint import pprint

import helpers.yaml_helper as yaml


def parse_spreadsheet(save_to_file: bool = False):
    with open('usc-ship-roster.csv', newline='', encoding='utf-8') as file:
        ships = []
        members = []
        reader = csv.reader(file, delimiter=',')
        line_count = 1

        for line in reader:
            if line_count == 1:
                line_count += 1
                continue

            if line[0]:
                if line[0] == 'USC Members':
                    ships = line[1:-1]
                else:
                    member_dict = {
                        'name': line[0],
                        'number': int(line[-1]),
                        'ships': [ships[index] for index, value in enumerate(line[1: -1]) if value]
                    }

                    members.append(member_dict)

            line_count += 1

        if save_to_file:
            yaml.save_to_yaml('usc-ship-roster', {'data': members, 'ships': ships})

    return {'members': members, 'ship_list': ships}


def get_user_ships(user: str = 'Ezoss'):
    data = parse_spreadsheet()['members']

    return next((member for member in data if member['name'] == user), None)


if __name__ == '__main__':
    parse_spreadsheet(save_to_file=True)
