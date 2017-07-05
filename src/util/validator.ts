/**
 * @license
 * Copyright (C) 2016-2017 Joseph Roque
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
 * @file validate.ts
 * @description Validates each json file with its schemas
 */

/** Interface for defining steps to validate config files. */
export interface Validation {
  name: string;
  require: any;
  schema: any;
}

/** Basic schema definition for validation. */
export interface BaseSchema {
  name: string;
  schema: any;
}

// Imports
import { Validator } from 'jsonschema';

/**
 * Runs schema validations over {validations}.
 *
 * @returns {boolean} true if all validations succeed, false otherwise.
 */
export function validate(): boolean {
  let valid = true;

  // Instance of Validator
  const validator = new Validator();

  // Import all basic definitions
  const schemas: BaseSchema[] = require('../assets/__schemas__');
  for (const schema of schemas) {
    validator.addSchema(schema.schema, schema.name);
  }

  // List of files to validate and their schemas
  let validations: Validation[] = [];

  // Compile the list of files to validate
  validations.push({
    name: 'config.json',
    require: require('../assets/config.json'),
    schema: require('../assets/__schemas__/config.schema.json'),
  });

  // Add the assets to validate
  const assets: Validation[] = require('../assets');
  validations = validations.concat(assets);

  for (const validation of validations) {
    const validationResults = validator.validate(validation.require, validation.schema);

    // Report any errors and continue validating
    if (validationResults.errors.length > 0) {
      console.error(`${validation.name} has not passed validation. Results below.`);
      console.error(validationResults.errors);
      valid = false;
    } else {
      console.log(`${validation.name} passed validation.`);
    }
  }

  return valid;
}
