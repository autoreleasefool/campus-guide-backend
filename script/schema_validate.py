#!/usr/bin/env python3

import json
import os
import re
import sys
import jsonschema

re_language = re.compile(r'[.][a-z]+$')
re_comment = re.compile(r'^\s*[/]{2}.*$', flags=re.MULTILINE)

success_code = 0

if len(sys.argv) < 3:
  print('Usage: ./schema_validate.py <asset_dir> <schema_dir>')
  sys.exit(2)

# Import base schemas
store = {}
base_schema_dir = os.path.join(sys.argv[2], '__base__')
for base_schema_name in os.listdir(base_schema_dir):
  with open(os.path.join(base_schema_dir, base_schema_name)) as base_schema_raw:
    base_schema = json.load(base_schema_raw)
    store[base_schema['id']] = base_schema

# Strip single line comments from a JSON file
def strip_comments(str_in):
  comment = re.search(re_comment, str_in)
  while comment:
    str_in = str_in[:comment.span()[0]] + str_in[comment.span()[1] + 1:]
    comment = re.search(re_comment, str_in)
  return str_in

# Validate a single file
def validate(config, schema_path, schema_name):
  config_json = schema_json = None
  with open(config) as file:
    config_json = json.loads(strip_comments(file.read()))
  with open(os.path.join(schema_path, schema_name)) as file:
    schema_json = json.loads(file.read())

  resolver = jsonschema.RefResolver('file://{0}/{1}'.format(schema_path, schema_name), schema_json, store)

  try:
    jsonschema.Draft4Validator(schema_json, resolver=resolver).validate(config_json)
    print('  Success: {0}'.format(config))
  except jsonschema.ValidationError as error:
    success_code = 1
    print('  Failed: `{0}`'.format(config))
    print('    {0}'.format(error.message))

# Validate all files in './assets/'
def validate_all(config_dir, schema_dir):
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
        language_pos = re.search(re_language, schema_name)
        if language_pos:
          schema_name = schema_name[:language_pos.span()[0]] + schema_name[language_pos.span()[1] + 1:]
        schema_name = '{0}.schema.json'.format(schema_name)

      validate(file_path, schema_path, schema_name)
    else:
      directories.append(file)

  for d in directories:
    d_path = os.path.join(config_dir, d)
    sd_path = os.path.join(schema_dir, d)

    # Recursively push assets in directories
    validate_all(d_path, sd_path)

validate_all(sys.argv[1], sys.argv[2])

sys.exit(success_code)
