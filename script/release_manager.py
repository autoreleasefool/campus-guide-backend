#!/usr/bin/env python3

"""
Update the S3 bucket with new config files and assets.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

import boto3


# Types of assets
ASSET_TYPES = {
    'json': ['.json'],
    'image': ['.png', '.gif', '.jpg'],
    'text': ['.txt'],
}


def build_empty_config(desc_en='', desc_fr=''):
    """
    Get a basic empty config. For consistency.

    :rtype:
        `dict`
    """
    return {
        'files': [],
        'lastUpdatedAt': int(time.time()),
        'whatsNew': {
            'description_en': desc_en,
            'description_fr': desc_fr,
        },
    }


def get_total_config_size(config):
    """
    Given a config file, determine the total size of assets, zipped assets, and the total of both.

    :param config:
        The config file to parse
    :type config:
        `dict`
    :rtype:
        `int`, `int`, `int`
    """
    total_base_size = total_zipped_size = 0
    for asset_details in config['files']:
        total_base_size += asset_details['size']
        if 'zsize' in asset_details:
            total_zipped_size += asset_details['zsize']
    return total_base_size, total_zipped_size, total_base_size + total_zipped_size


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
    for file_path in glob.iglob(os.path.join(asset_dir, '**', '*'), recursive=True):
        directory, filename = file_path[:file_path.rfind(os.path.sep) + 1], \
                              file_path[file_path.rfind(os.path.sep) + 1:]
        if filename.find('.') > 0 and 'config' not in filename:
            assets.append((directory, filename))
    assets.sort(key=lambda s: s[1])
    return assets


def get_asset_type(asset_name):
    """
    Gets the asset type from ASSET_TYPES of an asset given its name.

    :param asset_name:
        Name of the asset
    :type: asset_name:
        `str`
    :rtype:
        `str` or None
    """
    filetype = asset_name[asset_name.rfind('.'):].lower()
    for asset_type in ASSET_TYPES:
        if filetype in ASSET_TYPES[asset_type]:
            return asset_type
    return None


def build_dev_config(asset_dir, output_dir, app_config_dir, filename, description):
    """
    Builds a config for a dev environment.

    :param asset_dir:
        Location of assets in filesystem
    :type asset_dir:
        `str`
    :param output_dir:
        Output location for config file
    :type output_dir:
        `str`
    :param app_config_dir:
        Output location for assets for application bundling
    :type app_config_dir:
        `dict`
    :param filename:
        Output filename for config file
    :type filename:
        `str`
    :param description:
        Description of the update
    :type description:
        `dict`
    """
    # pylint:disable=R0914
    assets = get_all_assets(asset_dir)
    print('Retrieved {0} assets'.format(len(assets)))

    print('Creating output directory `{0}`'.format(output_dir))
    os.makedirs(output_dir)
    for platform in app_config_dir:
        print('Creating app asset directory `{0}`'.format(app_config_dir[platform]))
        if os.path.exists(app_config_dir[platform]):
            shutil.rmtree(app_config_dir[platform])
        os.makedirs(app_config_dir[platform])
    config_ios = build_empty_config(desc_en=description['en'], desc_fr=description['fr'])
    config_android = build_empty_config(desc_en=description['en'], desc_fr=description['fr'])

    for dev_asset in assets:
        asset_folder = dev_asset[0]
        asset_name = dev_asset[1]
        if asset_name[-3:] == '.gz':
            continue

        asset_type = get_asset_type(dev_asset[1])
        asset_zurl_exists = os.path.exists(os.path.join(asset_folder, '{}.gz'.format(asset_name)))

        for platform in app_config_dir:
            if not os.path.exists(os.path.join(app_config_dir[platform], asset_type)):
                os.makedirs(os.path.join(app_config_dir[platform], asset_type))
            shutil.copy(
                os.path.join(asset_folder, asset_name),
                os.path.join(app_config_dir[platform], asset_type, asset_name)
            )

        file_ios = {
            'name': '/{}'.format(asset_name),
            'size': os.path.getsize(os.path.join(asset_folder, asset_name)),
            'type': asset_type,
            'url': 'http://localhost:8080/{0}/{1}'.format(asset_type, asset_name),
            'version': 1,
        }
        file_android = {
            'name': '/{}'.format(asset_name),
            'size': os.path.getsize(os.path.join(asset_folder, asset_name)),
            'type': asset_type,
            'url': 'http://10.0.2.2:8080/{0}/{1}'.format(asset_type, asset_name),
            'version': 1,
        }

        if asset_zurl_exists:
            file_ios['zurl'] = 'http://localhost:8080/{0}/{1}'.format(
                asset_type,
                '{}.gz'.format(asset_name)
            )
            file_ios['zsize'] = os.path.getsize(os.path.join(asset_folder,
                                                             '{}.gz'.format(asset_name)))

        config_ios['files'].append(file_ios)
        config_android['files'].append(file_android)

    total_base_size, total_zipped_size, total_size = get_total_config_size(config_ios)
    print('Config total download size: {0}/{1} ({2})'.format(
        total_base_size / 1000,
        total_zipped_size / 1000,
        total_size / 1000
    ))

    filename_ios = '{0}.ios.{1}'.format(filename[:filename.rindex('.')],
                                        filename[filename.rindex('.') + 1:])
    filename_android = '{0}.android.{1}'.format(filename[:filename.rindex('.')],
                                                filename[filename.rindex('.') + 1:])
    print('Dumping iOS config to `{0}{1}`'.format(output_dir, filename_ios))
    with open(os.path.join(output_dir, filename_ios), 'w') as config_file:
        json.dump(config_ios, config_file, sort_keys=True, ensure_ascii=False, indent=2)
    if 'ios' in app_config_dir:
        print('Dumping iOS config to `{0}/{1}`'.format(app_config_dir['ios'], 'base_config.json'))
        with open(os.path.join(app_config_dir['ios'], 'base_config.json'), 'w') as config_file:
            json.dump(config_ios, config_file, sort_keys=True, ensure_ascii=False, indent=2)
    print('Dumping Android config to `{0}{1}`'.format(output_dir, filename_android))
    with open(os.path.join(output_dir, filename_android), 'w') as config_file:
        json.dump(config_android, config_file, sort_keys=True, ensure_ascii=False, indent=2)
    if 'android' in app_config_dir:
        print('Dumping Android config to `{0}/{1}`'.format(
            app_config_dir['android'],
            'base_config.json'))
        with open(os.path.join(app_config_dir['android'], 'base_config.json'), 'w') as config_file:
            json.dump(config_android, config_file, sort_keys=True, ensure_ascii=False, indent=2)


def get_most_recent_config(bucket):
    """
    Given an S3 bucket, find the most recent config file version in that bucket and return its
    version as an array of 3 integers. If no config files are found, returns [0, 0, 0].

    :param bucket:
        the S3 bucket to examine
    :type bucket:
        :class:S3.Bucket
    :rtype:
        `list` of `int`
    """
    objects = bucket.objects.all()
    max_version = [0, 0, 0]
    for item in objects:
        if item.key[:7] != 'config/' or len(item.key) <= 7:
            continue
        item_version = list(map(int, item.key.split('/')[1].split('.')[:3]))
        for i, _ in enumerate(item_version):
            if item_version[i] > max_version[i]:
                max_version = item_version
                break
    print('Found most recent config version: {0}'.format(max_version))
    return max_version


def get_release_config_version(bucket, version):
    """
    Gets a string for the config version to build.

    :param bucket:
        the s3 bucket to examine for the most recent config version, if necessary
    :type bucket:
        :class:S3.Bucket
    :param version:
        Either the major.minor.patch build number for the config, or
        'major', 'minor', or 'patch' to update from the most recent config version
    :type version:
        `str`
    """
    if re.match(r'[0-9]+[.][0-9]+[.][0-9]+', version):
        return version

    last_version = get_most_recent_config(bucket)
    if version == 'major':
        last_version[0] = last_version[0] + 1
        last_version[1] = 0
        last_version[2] = 0
    elif version == 'minor':
        last_version[1] = last_version[1] + 1
        last_version[2] = 0
    elif version == 'patch':
        last_version[2] = last_version[2] + 1
    else:
        raise ValueError('`version` must be one of "major", "minor", "patch", or match "X.Y.Z"')

    last_version = [str(x) for x in last_version]
    return '.'.join(last_version)


def update_asset(
        bucket,
        name,
        asset_type,
        content,
        version,
        zcontent=None,
        compatible=False,
        configs={},
        upload_file=True):
    """
    Upload an asset to S3 bucket. Override existing versions, and update any config files
    that contain the asset. Returns the URL to access the asset.

    :param bucket:
        S3 bucket to upload to
    :type bucket:
        :class:S3.Bucket
    :param dir:
        Directory containing asset
    :type dir:
        `str`
    :param name:
        Filename of the asset
    :type name:
        `str`
    :param asset_type:
        Type of the asset
    :type asset_type:
        `str`
    :param content:
        Content of the asset
    :type content:
        `str`
    :param version:
        Version number for asset
    :type version:
        `int`
    :param zcontent:
        Zipped content of the asset
    :type zcontent:
        `str`
    :param compatible:
        If True, then previous configs will be checked if they contain the file and their
        versions updated
    :type compatible:
        `bool`
    :param configs:
        List of existing configs to check and update
    :type:
        `list` of `json`
    :param upload_file:
        True to upload the file, false to skip
    :type upload_file:
        `bool`
    :rtype:
        `str`
    """
    # pylint:disable=W0102,R0912,R0913,R0914
    global S3      # pylint:disable=W0603
    global REGION  # pylint:disable=W0603

    content_type = 'application/json; charset=utf-8'
    if asset_type == 'image':
        if name[-3:] == 'png':
            content_type = 'image/png'
        elif name[-3:] == 'jpg':
            content_type = 'image/jpeg'
        elif name[-3:] == 'gif':
            content_type = 'image/gif'
    elif asset_type == 'text':
        content_type = 'text/plain; charset=utf-8'

    object_kwargs = {
        'ACL': 'public-read',
        'ContentType': content_type,
        'Metadata': {
            'version': str(version),
        },
    }

    if upload_file:
        print('Uploading asset `{0}`'.format('assets{0}'.format(name)))
        bucket.put_object(Key='assets{0}'.format(name), Body=content, **object_kwargs)

    base_object = S3.Object(bucket.name, 'assets{0}'.format(name)).get()
    size = base_object['ContentLength']
    version = int(base_object['Metadata']['version'])
    url = 'https://s3.{0}.amazonaws.com/{1}/assets{2}?versionId={3}'.format(
        REGION,
        bucket.name,
        name,
        base_object['VersionId']
    )

    updated_asset = {
        'size': size,
        'url': url,
        'version': version,
    }

    if zcontent:
        if upload_file:
            print('Uploading asset `{0}`'.format('assets{0}.gz'.format(name)))
            bucket.put_object(
                Key='assets{0}.gz'.format(name),
                Body=zcontent,
                ContentEncoding='gzip',
                **object_kwargs
            )
        zipped_object = S3.Object(bucket.name, 'assets{0}.gz'.format(name)).get()
        updated_asset['zsize'] = zipped_object['ContentLength']
        updated_asset['zurl'] = 'https://s3.{}.amazonaws.com/{}/assets{}.gz?versionId={}'.format(
            REGION,
            bucket.name,
            name,
            zipped_object['VersionId']
        )

    if compatible:
        for config in configs:
            updated = False
            for file in configs[config]['content']['files']:
                if file['name'] != name or file['version'] != version - 1:
                    continue
                file['size'] = updated_asset['size']
                file['url'] = updated_asset['url']
                file['version'] = version
                if 'zsize' in file:
                    if 'zsize' in updated_asset:
                        file['zsize'] = updated_asset['zsize']
                        file['zurl'] = updated_asset['zurl']
                    else:
                        file.pop('zsize', None)
                        file.pop('zurl', None)
                updated = True
            if updated:
                configs[config]['updated'] = True
                configs[config]['content']['lastUpdatedAt'] = int(time.time())
    return updated_asset


def parse_existing_config(item, existing_configs):
    """
    Parse the content of a config and add it to the existing configs.

    :param item:
        An object from S3
    :type item:
        :class:S3.Object
    :param existing_configs:
        The existing configs
    :type existing_configs:
        `dict`
    """
    item_key = item.key
    existing_config = item.get()
    existing_configs[item_key] = {
        'content': json.loads(existing_config['Body'].read()),
        'key': item_key,
        'updated': False,
    }
    print('Parsed existing config `{0}`'.format(item_key))


def parse_existing_asset(item, existing_assets):
    """
    Parse the content of an asset and add it to the existing assets.

    :param item:
        An object from S3
    :type item:
        :class:S3.Object
    :param existing_assets:
        The existing assets
    :type existing_assets:
        `dict`
    """
    item_key = item.key[6:]
    if item_key[-3:] == '.gz':
        item_key = item_key[:-3]
        existing_assets[item_key]['zipped'] = True
        return

    existing_asset = item.get()
    existing_assets[item_key] = {
        'content': existing_asset['Body'].read(),
        'version': existing_asset['Metadata']['version'],
        'versionId': existing_asset['VersionId'],
        'zipped': False,
    }
    print('Parsed existing asset `{0}`'.format(item_key))


def update_changed_assets(bucket, asset_dir, output_dir, only, compatible=False):
    """
    Update assets which have changed from those versions already in the bucket. Also upload new
    assets not yet in the bucket. Returns a dict with updated assets and a dict of configs which
    may or may not have been updated due to the new assets.

    :param bucket:
        An S3 bucket to retrieve existing assets and configs from
    :type bucket:
        :class:S3.Bucket
    :param asset_dir:
        Asset directory
    :type asset_dir:
        `str`
    :param output_dir:
        Output directory for minified assets and config
    :type output_dir:
        `str`
    :param only:
        Set of asset names which should be updated, and all others skipped, or None.
    :type only:
        `set`
    :param compatible:
        If True, update existing configs to accept the new version.
    :type compatible:
        `bool`
    :rtype:
        `dict`, `dict`
    """
    # pylint:disable=R0914
    # Minify assets
    print('Cleaning output directory `{0}'.format(output_dir))
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    print('Beginning minify subprocess, from `{0}` to `{1}`'.format(asset_dir, output_dir))
    subprocess.run(['./script/minify.sh', asset_dir, output_dir])

    # Get existing assets from bucket
    bucket_objects = bucket.objects.all()
    existing_assets = {}
    existing_configs = {}
    for item in bucket_objects:
        if item.key[:7] == 'config/' and len(item.key) > 7:
            parse_existing_config(item, existing_configs)
        elif item.key[:7] == 'assets/' and len(item.key) > 7:
            parse_existing_asset(item, existing_assets)

    # Get local assets and filter for only those specified to be updated
    assets = get_all_assets(output_dir)
    assets = [x for x in assets if only is None or '/{}'.format(x[1]) in only]
    print('Retrieved {0} assets'.format(len(assets)))

    changed_assets = {}
    for existing_asset in assets:
        asset_folder = existing_asset[0]
        asset_name = existing_asset[1]
        slash_asset_name = '/{}'.format(asset_name)
        asset_type = get_asset_type(existing_asset[1])

        if asset_name[-3:] == '.gz':
            continue

        last_version = 0
        asset_content = None
        asset_zcontent = None
        upload_file = True
        with open(os.path.join(asset_folder, asset_name), 'rb') as asset_file:
            asset_content = asset_file.read()
        if os.path.exists(os.path.join(asset_folder, '{}.gz'.format(asset_name))):
            with open(os.path.join(asset_folder, '{}.gz'.format(asset_name)), 'rb') as asset_zfile:
                asset_zcontent = asset_zfile.read()
        if slash_asset_name in existing_assets:
            if existing_assets[slash_asset_name]['content'] == asset_content:
                upload_file = False
            else:
                last_version = int(existing_assets[slash_asset_name]['version'])

        asset_details = update_asset(
            bucket,
            slash_asset_name,
            asset_type,
            asset_content,
            last_version + 1,
            zcontent=asset_zcontent,
            compatible=compatible,
            configs=existing_configs,
            upload_file=upload_file
        )
        built_asset = {
            'name': slash_asset_name,
            'size': asset_details['size'],
            'type': asset_type,
            'url': asset_details['url'],
            'version': asset_details['version'],
        }

        if 'zurl' in asset_details and 'zsize' in asset_details:
            built_asset['zsize'] = asset_details['zsize']
            built_asset['zurl'] = asset_details['zurl']

        changed_assets[slash_asset_name] = built_asset

    return changed_assets, existing_configs


def build_release_config(assets, version, description):
    """
    Build a config for release.

    :param bucket:
        An S3 bucket to retrieve existing assets and configs from
    :type bucket:
        :class:S3.Bucket
    :param assets:
        Asset names and details for the config
    :type assets:
        `dict`
    :param version:
        Version for config
    :type version:
        `int`
    :param description:
        Description of the update
    :type description:
        `dict`
    :rtype:
        `str`, `dict`
    """
    config = build_empty_config(desc_en=description['en'], desc_fr=description['fr'])
    for release_asset in assets:
        config['files'].append(assets[release_asset])
    config_key = 'config/{0}.json'.format(version)
    config_details = {
        'content': config,
        'key': config_key,
        'updated': True,
    }
    print('Built config file `{0}`'.format(config_key))
    total_base_size, total_zipped_size, total_size = get_total_config_size(config)
    print('Config total download size: {0}/{1} ({2})'.format(
        total_base_size / 1000,
        total_zipped_size / 1000,
        total_size / 1000
    ))
    return config_key, config_details


def update_changed_configs(bucket, configs):
    """
    Update only config files in `configs` which have the key 'updated' set to True.

    :param bucket:
        S3 bucket which all configs exist in
    :type bucket:
        :class:S3.Bucket
    :param configs:
        Dictionary of config names and details
    :type configs:
        `dict`
    """
    for config in configs:
        if not configs[config]['updated']:
            continue
        print('Uploading config `{0}`'.format(configs[config]['key']))
        bucket.put_object(
            Key=configs[config]['key'],
            Body=json.dumps(configs[config]['content']),
            ACL='public-read'
        )

DESCRIPTION = {'en': '', 'fr': ''}

# Input validation
if len(sys.argv) >= 2 and sys.argv[1] == '--dev':
    DEV_ASSET_DIR = '../assets_dev/' if len(sys.argv) < 3 else sys.argv[2]
    DEV_OUTPUT_DIR = '../assets_dev/config' if len(sys.argv) < 4 else sys.argv[3]
    DEV_FILENAME = 'public.json' if len(sys.argv) < 5 else sys.argv[4]
    DEV_APP_DIR = {}
    if '--ios' in sys.argv:
        DEV_APP_DIR['ios'] = sys.argv[sys.argv.index('--ios') + 1]
    if '--android' in sys.argv:
        DEV_APP_DIR['android'] = sys.argv[sys.argv.index('--android') + 1]
    if '--desc' in sys.argv:
        desc_idx = sys.argv.index('--desc')
        DESCRIPTION = {'en': sys.argv[desc_idx + 1], 'fr': sys.argv[desc_idx + 2]}
    else:
        DESCRIPTION = {'en': 'Test update.', 'fr': 'Mise à jour test.'}

    build_dev_config(DEV_ASSET_DIR, DEV_OUTPUT_DIR, DEV_APP_DIR, DEV_FILENAME, DESCRIPTION)
    exit()
elif len(sys.argv) < 5:
    print('\n\tCampus Guide - Release Manager')
    print('\tUsage:   release_manager.py', end='')
    print(' <bucket_name> <asset_dir> <output_dir> <#.#.#|major|minor|patch> [options]')
    print('\tAlt:     release_manager.py', end='')
    print(' --dev <asset_dir> <config_dir> <config_name>', end='')
    print(' [--ios <config_dir>]', end='')
    print(' [--android <config_dir>]')
    print('\tExample: release_manager.py', end='')
    print(' <bucket_name> assets/ assets_release/ patch [options]')
    print('\tOptions:')
    print('\t--dev\t\t\tBuild a config file for dev based on the given directory')
    print('\t--no-new-config\t\tPush changed assets and only update configs which exist')
    print('\t--only <name1,...>\tUpdate only assets with the given names. Otherwise, update all')
    print('\t--region <region>\tAWS region')
    print('\t--compatible\t\tSpecify that assets changed are compatible with existing configs')
    print('\t--desc <en> <fr>\tEnglish and French descriptions of the config changes')
    print()
    exit()

# Parse arguments
BUCKET_NAME = sys.argv[1]
ASSET_DIR = sys.argv[2]
OUTPUT_DIR = sys.argv[3]
NEW_VERSION = sys.argv[4]
BUILD_CONFIG = True
REGION = 'ca-central-1'
ONLY_UPGRADE = None
COMPATIBLE = False

SKIP_ARGS = 0
if len(sys.argv) > 5:
    for (index, arg) in enumerate(sys.argv[5:]):
        if SKIP_ARGS > 0:
            SKIP_ARGS -= 1
            continue

        if arg == '--only':
            SKIP_ARGS = 1
            ONLY_UPGRADE = set()
            for asset in sys.argv[index + 1].split(','):
                ONLY_UPGRADE.add(asset)
        elif arg == '--region':
            SKIP_ARGS = 1
            REGION = sys.argv[index + 1]
        elif arg == '--no-new-config':
            BUILD_CONFIG = False
        elif arg == '--compatible':
            COMPATIBLE = True
        elif arg == '--desc':
            DESCRIPTION = {
                'en': sys.argv[index + 1],
                'fr': sys.argv[index + 2],
            }
            SKIP_ARGS = 2

S3 = boto3.resource('s3')
BUCKET = S3.Bucket(BUCKET_NAME)

UPDATED_ASSETS, UPDATED_CONFIGS = update_changed_assets(
    BUCKET, ASSET_DIR, OUTPUT_DIR, ONLY_UPGRADE, compatible=COMPATIBLE)

if COMPATIBLE:
    update_changed_configs(BUCKET, UPDATED_CONFIGS)
if BUILD_CONFIG:
    CONFIG_VERSION = get_release_config_version(BUCKET, NEW_VERSION)
    CONFIG_KEY, CONFIG_DETAILS = build_release_config(UPDATED_ASSETS, CONFIG_VERSION, DESCRIPTION)
    update_changed_configs(BUCKET, {CONFIG_KEY: CONFIG_DETAILS})
