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
 * @file server.js
 * @description Provides main server functionality and routing.
 *
 * @flow
 */
'use strict';

// Imports
const Validator = require('jsonschema').Validator;

// Print out startup time to default logs
console.log('--------------------------------');
console.log('Starting new instance of server.');
console.log(new Date());
console.log('--------------------------------');

// Print out startup time to error
console.error('--------------------------------');
console.error('Starting new instance of server.');
console.error(new Date());
console.error('--------------------------------');

// Port that server will run on
const PORT = 8080;
// List of available file configurations
const CONFIG = require('./json/config.json');

// Ensure the configuration file follows the defined schema
const configValidator = new Validator();
const configurationSchema = require('./json/config.schema.json');
const validatorResults = configValidator.validate(CONFIG, configurationSchema);

if (validatorResults.errors.length > 0) {
  console.error('./json/config.json failed to pass validation. Results below.');
  console.error(validatorResults);
  process.exit(1);
}

