import csv
from pprint import pprint

import helpers.yaml_helper as yaml
import helpers.database as db

ship_table = db.Table('usc_ships', 'user')


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
    return ship_table.get_item(user)


def add_ships(user, *ships):
    data = ship_table.get_item(user)
    existing_ships = data['ships']
    ship_number = data['ship_number']
    results = {
        'added': [],
        'unsuccessful': []
    }

    for ship in ships:
        if ship in existing_ships:
            continue

        if ship not in yaml.read_yaml('usc-ship-roster')['ships']:
            results['unsuccessful'].append(ship)
            continue

        existing_ships.append(ship)
        results['added'].append(ship)

        ship_number += 1

    ship_table.update_item(user, ships=existing_ships, ship_number=ship_number)

    return results


def remove_ships(user, *ships):
    data = ship_table.get_item(user)
    existing_ships = data['ships']
    ship_number = data['ship_number']
    results = {
        'removed': [],
        'unsuccessful': []
    }

    for ship in ships:
        if ship not in existing_ships:
            results['unsuccessful'].append(ship)
            continue

        existing_ships.remove(ship)
        ship_number -= 1

        results['removed'].append(ship)

    ship_table.update_item(user, ships=existing_ships, ship_number=ship_number)

    return results


if __name__ == '__main__':
    parse_spreadsheet(save_to_file=True)
    # data = yaml.read_yaml('usc-ship-roster')
    #
    # for member in data['data']:
    #     ship_table.update_item(member['name'], ships=member['ships'])
