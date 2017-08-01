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
    print('\t--add, -a\t\tRegister new assets')
    print('\t--remove, -r\t\tRemove assets')
    print('\t--update-sizes\t\tUpdate asset sizes')
    print('\t--all or --newest\tDirect script to update all config files, or only the newest')
    print('\t-b <dir>\t\tBase directory to assets/ and assets_min/. Default `.`')
    exit()

ASSET_TYPES = {
    'json': ['.json'],
    'image': ['.png', '.gif', '.jpg'],
    'text': ['.txt'],
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
    if asset_type in ['json', 'text']:
        return asset_type
    return '{}s'.format(asset_type)


def get_all_assets(asset_dir):
    """
    Get all available asset names in the base directory and the subdirectory they are in.
    First item in tuple is the asset directory, second is the asset name.

    :param asset_dir:
        Base directory to begin search from
    :type asset_dir:
        `str`
    :rtype:
        `list` of (`str`, `str`)
    """
    assets = []
    directories = []
    for file in os.listdir(asset_dir):
        file_path = os.path.join(asset_dir, file)
        if os.path.isfile(file_path):
            if not file.startswith('.') and 'config' not in file_path:
                assets.append((asset_dir, file))
        else:
            directories.append(file_path)
    for directory in directories:
        assets += get_all_assets(directory)
    return assets


def get_all_configs(base_dir):
    """
    Get the base config directories, and a list of the names of all existing config files.

    :param base_dir:
        Base directory for configs
    :type base_dir:
        `str`
    :rtype:
        `list` of `str`, `list` of `str`
    """
    config_dir = os.path.join(base_dir, 'assets', 'config')
    config_dir_min = os.path.join(base_dir, 'assets_min', 'config')
    configs = os.listdir(config_dir)
    return [config_dir, config_dir_min], configs


def update_asset_sizes(all_configs, base_dir):
    """
    Update size of assets in the relative configuration files.

    :param all_configs:
        True to update the size of all present assets in all config files which they appear in.
        False to only update in the most recent config file.
    :type all_configs:
        `bool`
    :param base_dir:
        Base directory for assets
    :type base_dir:
        `str`
    """
    if all_configs is None:
        print('Must specify --all or --newest for --update-sizes')
        return

    assets = get_all_assets(os.path.join(base_dir, 'assets_min'))
    config_dirs, configs = get_all_configs(base_dir)

    assets.sort(key=lambda s: s[1])
    configs.sort(key=lambda s: list(map(int, s.split('.')[:3])))
    if not all_configs:
        configs = configs[:1]

    for config in configs:
        print('Updating {}'.format(os.path.join(config_dirs[0], config)))
        with open(os.path.join(config_dirs[0], config)) as config_file:
            config_json = json.loads(config_file.read(), object_pairs_hook=OrderedDict)

            for asset in assets:
                for config_file in config_json['files']:
                    if '/{}'.format(asset[1]) == config_file['name']:
                        size = os.path.getsize(os.path.join(asset[0], asset[1]))
                        config_file['size'] = size

                        zipped_path = os.path.join(asset[0], '{}.gz'.format(asset[1]))
                        if os.path.exists(zipped_path):
                            zsize = os.path.getsize(zipped_path)
                            config_file['zsize'] = zsize
                            config_file['zurl'] = True

            config_json['lastUpdatedAt'] = int(time.time())
            with open(os.path.join(config_dirs[0], config), 'w', encoding='utf8') as file:
                json.dump(config_json, file, sort_keys=True, ensure_ascii=False, indent=2)
            with open(os.path.join(config_dirs[1], config), 'w', encoding='utf8') as file:
                json.dump(config_json, file, sort_keys=True, ensure_ascii=False)


def process_asset_modification(should_remove, asset_name, base_dir):
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
    :param base_dir:
        Base directory for assets
    :type base_dir:
        `str`
    """
    # pylint:disable=too-many-branches,too-many-statements
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
                os.remove(os.path.join(base_dir, 'assets', 'json', asset_name))
            except OSError:
                pass

            try:
                os.remove(os.path.join(base_dir, 'assets_schemas', 'json', '{}.schema{}'.format(
                    asset_name_without_type,
                    asset_name_type_only,
                )))
            except OSError:
                pass
        else:
            print('Place json in ./assets/json/{0}'.format(asset_name))
            print('Place schema in ./assets_schemas/json/{0}.schema{1}'.format(
                asset_name_without_type,
                asset_name_type_only,
            ))
    elif asset_type == 'text':
        if should_remove:
            try:
                os.remove(os.path.join(base_dir, 'assets', 'text', asset_name))
            except OSError:
                pass
        else:
            print('Place text in ./assets/text/{0}'.format(asset_name))
    elif asset_type == 'image':
        if should_remove:
            try:
                os.remove(os.path.join(base_dir, 'assets', 'images', asset_name))
            except OSError:
                pass
        else:
            print('Place image in ./assets/images/{0}'.format(asset_name))

    config_dirs, configs = get_all_configs(base_dir)
    configs.sort(key=lambda s: list(map(int, s.split('.')[:3])))
    config_json = None
    with open(os.path.join(config_dirs[0], configs[0])) as config:
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
                'url': 'http://localhost:8080/{}/{}'.format(
                    pluralize_type(asset_type),
                    asset_name,
                ),
                'version': 1,
            })
            config_json['lastUpdatedAt'] = int(time.time())

    config_json['files'].sort(key=lambda x: (x['type'], x['name']))
    with open(os.path.join(config_dirs[0], configs[0]), 'w', encoding='utf8') as file:
        json.dump(config_json, file, sort_keys=True, ensure_ascii=False, indent=2)
    with open(os.path.join(config_dirs[1], configs[0]), 'w', encoding='utf8') as file:
        json.dump(config_json, file, sort_keys=True, ensure_ascii=False)

    if should_remove:
        print('* Finished removing asset {}'.format(asset_name))
    else:
        print('* Finished adding asset {}'.format(asset_name))

# Process arguments
REMOVE = 'remove'
ADD = 'add'
UPDATE_SIZES = 'update'
ALL = None
BASE_DIRECTORY = '.'

ARGUMENT_STATE = None

SKIP_NEXT = False
for (index, arg) in enumerate(sys.argv):
    if SKIP_NEXT:
        SKIP_NEXT = False
        continue

    if arg in ['--add', '-a']:
        ARGUMENT_STATE = ADD
    elif arg in ['--remove', '-r']:
        ARGUMENT_STATE = REMOVE
    elif arg == '--update-sizes':
        ARGUMENT_STATE = UPDATE_SIZES
    elif arg in ['--all', '--newest']:
        ALL = arg == '-all'
    elif arg == '-b':
        BASE_DIRECTORY = sys.argv[index + 1]
        SKIP_NEXT = True
    elif ARGUMENT_STATE == ADD:
        process_asset_modification(False, arg, BASE_DIRECTORY)
    elif ARGUMENT_STATE == REMOVE:
        process_asset_modification(True, arg, BASE_DIRECTORY)

if ARGUMENT_STATE == UPDATE_SIZES:
    update_asset_sizes(ALL, BASE_DIRECTORY)
