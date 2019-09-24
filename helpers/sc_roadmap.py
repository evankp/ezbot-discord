import requests
import yaml
from datetime import datetime, timedelta

import helpers.yaml_helper as yaml_functions
from helpers.time import last_update_date


def get_releases_raw(output: str = 'dict'):
    resp = requests.get('https://robertsspaceindustries.com/api/roadmap/v1/boards/1').json()

    if output == 'file':
        file_name = f'patch-data/sc-roadmap-data-{last_update_date()}.yaml'

        with open(file_name, 'w') as file:
            yaml.safe_dump(resp['data']['releases'], file)

        return

    return resp['data']['releases']


# Parse individual patches
def parse_patch_progress(patch):
    if patch:
        categories = []

        for card in patch['cards']:
            id = card['url_slug'].lower()
            category = {
                'name': card['name'],
                'id': id,
                'description': card['description'],
                'status': 'Polishing' if card['completed'] == card['tasks'] else 'In Progress',
                'thumbnail': f"https://robertsspaceindustries.com{card['thumbnail']['urls']['square']}"
            }

            if category['status'] == 'In Progress':
                category['progress'] = '{:.2%}'.format(card['completed'] / card['tasks'])

            categories.append(category)

        return {
            'categories': categories,
            'patch': patch
        }


# Parse all patches not released
def get_releases_parsed(output: str = 'list'):
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
        yaml_functions.save_to_yaml(f'patch-data/patches-parsed-{last_update_date()}', patches)
        with open(f'patch-data/patches-parsed-{last_update_date()}.yaml', 'w') as file:
            yaml.safe_dump(patches, file, sort_keys=False)

        return

    return patches


def compare_patch_differences(old_data=None, new_data=None, output: str = 'dict'):
    total_changes = []

    old_file = f"patch-data/patches-parsed-{(last_update_date(datetime_obj=True) - timedelta(weeks=1)).strftime('%m-%d-%Y')}"
    new_file = f"patch-data/patches-parsed-{last_update_date()}"

    try:
        if old_data is None:
            old_data = yaml_functions.read_yaml(old_file)

        if new_data is None:
            new_data = yaml_functions.read_yaml(new_file)
    except FileNotFoundError as error:
        return {'error': str(error)}

    for new_patch in new_data:
        patch_name = new_patch['patch']
        old_patch = None
        patch_changes = {}

        # Get same patch data object
        for patch in old_data:
            if patch['patch'] != patch_name:
                continue

            old_patch = patch

        # If patch is not in old data, pass for now.
        if old_patch is None:
            continue

        # Compare new IDs with old ids to see if any was added or removed
        new_ids = [item['id'] for item in new_patch['categories']]
        old_ids = [item['id'] for item in old_patch['categories']]

        patch_changes['added'] = [id for id in new_ids if id not in old_ids]
        patch_changes['removed'] = [id for id in old_ids if id not in new_ids]

        # Check categories for any updates
        patch_changes['updated'] = []
        for category in new_patch['categories']:
            if category['id'] in patch_changes['added'] or category['id'] in patch_changes['removed']:
                continue

            old_category = next((item for item in old_patch['categories'] if item['id'] == category['id']), None)

            category_changes = category.items() - old_category.items()
            if category_changes:
                category_updates = {
                    'category': category['id'],
                    'attribute_updates': []
                }

                for change in category_changes:
                    old_attr = None

                    try:
                        old_attr = old_category[change[0]]
                    except KeyError:
                        pass

                    category_updates['attribute_updates'].append(
                        {'attribute': change[0], 'old': old_attr, 'new': change[1]})
                patch_changes['updated'].append(category_updates)

        # Add patch changes to global patch change list
        total_changes.append({'patch': patch_name, 'changes': patch_changes})

    if output == 'file':
        file = f"patch-data/roadmap-update-{last_update_date()}"
        yaml_functions.save_to_yaml(file,
                                    {'date': last_update_date(datetime_obj=True).timestamp(), 'updates': total_changes})

        return f'Saved to {file}.yaml'

    return {'date': datetime.now().timestamp(), 'updates': total_changes}


def get_latest_patch_updates(patch=None):
    try:
        update = yaml_functions.read_yaml(f'patch-data/roadmap-update-{last_update_date()}')
    except FileNotFoundError:
        return {'error': 'Not enough data collected for updates yet!'}

    if patch:
        return {'date': update['date'],
                'updates': next((update['changes'] for update in update['updates'] if update['patch'] == patch), None)}

    return update


if __name__ == '__main__':
    print(get_releases_parsed())

    # print(get_releases_raw('file'))
    # print(compare_patch_differences(
    #     old_data=yaml_functions.read_yaml('patches-parsed-09-16-2019'),
    #     new_data=yaml_functions.read_yaml('patches-parsed-09-20-2019'),
    #     output='file'
    # ))
