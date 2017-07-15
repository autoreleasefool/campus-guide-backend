#!/usr/bin/env python3

"""
Manage assets in the campus guide. Add or remove assets from the
configuration definition easily.
"""

import json
import os
import sys
import time
from collections import OrderedDict

# Instructions
if len(sys.argv) == 1:
    print('\n\tCampus Guide - asset manager')
    print('\t--add, -a\t\t Register new assets')
    print('\t--remove, -r\t\t Remove assets')
    exit()

ASSET_TYPES = {
    'json': ['.json'],
    'image': ['.png', '.gif', '.jpg'],
}

def pluralize_type(asset_type):
    """
    Pluralizes asset types.

    :param asset_type:
        Type to pluralize
    :type asset_type:
        `str`
    :rtype:
        `str`
    """
    if asset_type == 'json':
        return 'json'
    else:
        return '{}s'.format(asset_type)

def process_asset(should_remove, asset_name):  #pylint:disable=R0912
    """
    Add or remove an asset from the application config.

    :param should_remove:
        True to remove an asset, false to add
    :type should_remove:
        `bool`
    :param asset_name:
        Name of the asset
    :type asset_name:
        `str`
    """
    asset_name_without_type = asset_name[:asset_name.rfind('.')]
    asset_name_type_only = asset_name[asset_name.rfind('.'):]
    asset_config_name = '/{}'.format(asset_name)
    asset_type = None
    for possible_asset_type in ASSET_TYPES:
        for filetype in ASSET_TYPES[possible_asset_type]:
            if asset_name_type_only == filetype:
                asset_type = possible_asset_type
                break

        if asset_type is not None:
            break

    if asset_type is None:
        print('Invalid asset type. Valid types are:')
        for asset_type in ASSET_TYPES:
            print('\t{}: {}'.format(asset_type, ', '.join(ASSET_TYPES[asset_type])))
        exit()
    elif asset_type == 'json':
        if should_remove:
            try:
                os.remove('./assets/json/{}'.format(asset_name))
            except OSError:
                pass

            try:
                os.remove('./assets_schemas/json/{}.schema{}'.format(
                    asset_name_without_type,
                    asset_name_type_only,
                ))
            except OSError:
                pass
        else:
            print('Place json in ./assets/json/{0}'.format(asset_name))
            print('Place schema in ./assets_schemas/json/{0}.schema{1}'.format(
                asset_name_without_type,
                asset_name_type_only,
            ))
    elif asset_type == 'image':
        if should_remove:
            try:
                os.remove('./assets/images/{}'.format(asset_name))
            except OSError:
                pass
        else:
            print('Place image in ./assets/images/{0}'.format(asset_name))

    configs = os.listdir(os.path.join('.', 'assets', 'config'))
    configs.sort(key=lambda s: list(map(int, s.split('.')[:3])))
    config_json = None
    with open(os.path.join('.', 'assets', 'config', configs[0])) as config:
        config_json = json.loads(config.read(), object_pairs_hook=OrderedDict)
        if should_remove:
            for (index, config) in enumerate(config_json):
                if config['name'] == asset_config_name:
                    config_json = config_json[:index] + config_json[index + 1:]
                    break
        else:
            config_json['files'].append({
                'name': asset_config_name,
                'type': asset_type,
                'url': '{}file_server{}/assets/{}/{}'.format(
                    '{',
                    '}',
                    pluralize_type(asset_type),
                    asset_name,
                ),
                'version': 1,
            })
            config_json['lastUpdatedAt'] = int(time.time())

    config_json['files'].sort(key=lambda x: (x['type'], x['name']))
    with open(os.path.join('.', 'assets', 'config', configs[0]), 'w', encoding='utf8') as f:
        json.dump(config_json, f, sort_keys=True, ensure_ascii=False, indent=2)

    if should_remove:
        print('* Finished removing asset {}'.format(asset_name))
    else:
        print('* Finished adding asset {}'.format(asset_name))

# Process arguments
adding_assets = False
removing_assets = False
for arg in sys.argv:
    if arg in ['--add', '-a']:
        adding_assets = True
        removing_assets = False
    elif arg in ['--remove', '-r']:
        adding_assets = False
        removing_assets = True
    else:
        if adding_assets:
            process_asset(False, arg)
        elif removing_assets:
            process_asset(True, arg)
