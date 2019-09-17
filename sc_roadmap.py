import requests
import yaml
from datetime import datetime


def get_releases_raw(output: str = 'dict'):
    resp = requests.get('https://robertsspaceindustries.com/api/roadmap/v1/boards/1').json()

    if output == 'file':
        with open(f'sc-roadmap-data-{datetime.now().date().strftime("%m-%d-%Y")}.yaml', 'w') as file:
            yaml.safe_dump(resp['data']['releases'], file)

        return

    return resp['data']['releases']


def parse_patch_progress(patch):
    if patch:
        categories = []

        for card in patch['cards']:
            id = card['url_slug'].lower()
            category = {
                'name': card['name'],
                'id': id,
                'description': card['description'],
                'status': 'Polishing' if card['completed'] == card['tasks'] else 'In Progress'
            }

            if category['status'] == 'In Progress':
                category['progress'] = '{:.2%}'.format(card['completed'] / card['tasks'])

            categories.append(category)

        return {
            'categories': categories,
            'patch': patch
        }


def get_releases_parsed(output: str = 'dict'):
    patches = []
    data = get_releases_raw()
    for patch in data:
        if patch['released'] or not patch['cards']:
            continue

        patch_data = parse_patch_progress(patch)

        patch_dict = {
            'patch': patch['name'],
            'release_quarter': patch['description'],
            'items_completed': len(
                [category for category in patch_data['categories'] if category['status'] == 'Polishing']
            ),
            'items': len(patch_data['categories']),
            'categories': patch_data['categories'],
        }

        patches.append(patch_dict)

    if output == 'file':
        with open(f'patches-parsed-{datetime.now().date().strftime("%m-%d-%Y")}.yaml', 'w') as file:
            yaml.safe_dump(patches, file, sort_keys=False)

        return

    return patches


if __name__ == '__main__':
    get_releases_parsed('file')
