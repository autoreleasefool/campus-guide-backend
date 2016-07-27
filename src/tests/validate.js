/**
 *
 * @license
 * Copyright (C) 2016 Joseph Roque
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @author Joseph Roque
 * @file validate.js
 * @description Validates each json file with its schemas
 *
 * @flow
 */
'use strict';

export type Validation = {
  name: string,
  require: Object,
  schema: Object,
};

// Imports
const fs = require('fs');
const path = require('path');
const Validator = require('jsonschema').Validator;

/**
 * Runs schema validations over {validations}.
 *
 * @returns {boolean} true if all validations succeed, false otherwise.
 */
function validate(): boolean {
  let valid: boolean = true;

  // Instance of Validator
  const validator = new Validator();

  // List of files to validate and their schemas
  let validations: Array < Validation > = [];

  // Compile the list of files to validate
  validations.push({
    name: './src/json/config.json',
    require: require('../json/server_config.json'),
    schema: require('../json/__schemas__/server_config.schema.json'),
  });

  // Add the assets to validate, if they are present
  try {
    fs.accessSync(path.join('./build/assets/index.js'), fs.F_OK);
    const assets: Array < Validation > = require('../assets');
    validations = validations.concat(assets);
  } catch (e) {
    console.log('Assets not found. Continuing without them.');
  }

  for (let i = 0; i < validations.length; i++) {
    const validation: Validation = validations[i];
    const validationResults = validator.validate(validation.require, validation.schema);

    // Report any errors and continue validating
    if (validationResults.errors.length > 0) {
      console.error(validation.name + ' has not passed validation. Results below.');
      console.error(validationResults.errors);
      valid = false;
    } else {
      console.log(validation.name + ' passed validation.');
    }
  }

  return valid;
}

module.exports = validate;
