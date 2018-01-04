#!/usr/bin/env python3

"""
Validate configuration files using the provided schemas.
"""

import json
import os
import re
import sys
import jsonschema

RE_LANGUAGE = re.compile(r'[.][a-z]+$')
RE_COMMENT = re.compile(r'^\s*[/]{2}.*$', flags=re.MULTILINE)

SUCCESS_CODE = 0

if len(sys.argv) < 3:
    print('Usage: ./schema_validate.py <asset_dir> <schema_dir>')
    SUCCESS_CODE = 2
    sys.exit(SUCCESS_CODE)

# Import base schemas
STORE = {}
BASE_SCHEMA_DIR = os.path.join(sys.argv[2], '__base__')
for base_schema_name in os.listdir(BASE_SCHEMA_DIR):
    with open(os.path.join(BASE_SCHEMA_DIR, base_schema_name)) as base_schema_raw:
        base_schema = json.load(base_schema_raw)
        STORE[base_schema['id']] = base_schema


def set_success_code(code):
    """
    Set the success code for the program.

    :param code:
        New code
    :type code:
        `int`
    """
    global SUCCESS_CODE  # pylint:disable=global-statement
    SUCCESS_CODE = code


def strip_comments(str_in):
    """
    Remove single line comments from a multiline string.

    :param str_in:
        Input string
    :type str_in:
        `str`
    :rtype:
        `str`
    """
    comment = re.search(RE_COMMENT, str_in)
    while comment:
        str_in = str_in[:comment.span()[0]] + str_in[comment.span()[1] + 1:]
        comment = re.search(RE_COMMENT, str_in)
    return str_in


def validate(config, schema_path, schema_name):
    """
    Validate a single configuration file using the schema at the provided path,
    with the provided name.

    :param config:
        Location of the config file
    :type config:
        `str`
    :param schema_path:
        Location of the schema
    :type schema_path:
        `str`
    :param schema_name:
        Name of the schema file
    :type schema_name:
        `str`
    """
    config_json = schema_json = None
    with open(config) as file:
        config_json = json.loads(strip_comments(file.read()))
    with open(os.path.join(schema_path, schema_name)) as file:
        schema_json = json.loads(file.read())

    resolver = jsonschema.RefResolver(
        'file://{0}/{1}'.format(schema_path, schema_name),
        schema_json,
        STORE,
    )

    try:
        jsonschema.Draft4Validator(schema_json, resolver=resolver).validate(config_json)
        print('  Success: {0}'.format(config))
    except jsonschema.ValidationError as error:
        set_success_code(1)
        print('  Failed: `{0}`'.format(config))
        print('    {0}'.format(error.message))


def validate_all(config_dir, schema_dir):
    """
    Validate all files in a directory.

    :param config_dir:
        The base directory of configuration files
    :type config_dir:
        `str`
    :param schema_dir:
        The base directory of schema files to validate with
    :type schema_dir:
        `str`
    """
    directories = []
    print('Beginning validation of `{0}`'.format(config_dir))

    for file in os.listdir(config_dir):
        file_path = os.path.join(config_dir, file)
        if os.path.isfile(file_path):
            if not file_path.endswith('.json'):
                print('  Skipping `{0}`'.format(file_path))
                continue

            schema_path = schema_name = None

            # Use specific schema for app config files
            if re.search(os.path.join(sys.argv[1], 'config'), file_path):
                schema_path = os.path.join(sys.argv[2], 'config')
                schema_name = 'config.schema.json'
            else:
                # Strip filetype and language modifier
                schema_path = schema_dir
                schema_name = file[:file.index('.json')]
                language_pos = re.search(RE_LANGUAGE, schema_name)
                if language_pos:
                    schema_name = schema_name[:language_pos.span()[0]] + \
                                  schema_name[language_pos.span()[1] + 1:]
                schema_name = '{0}.schema.json'.format(schema_name)

            validate(file_path, schema_path, schema_name)
        else:
            directories.append(file)

    for directory in directories:
        d_path = os.path.join(config_dir, directory)
        sd_path = os.path.join(schema_dir, directory)

        # Recursively push assets in directories
        validate_all(d_path, sd_path)


validate_all(sys.argv[1], sys.argv[2])

sys.exit(SUCCESS_CODE)
