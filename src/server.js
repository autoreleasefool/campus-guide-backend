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
const Logging = require('./utils/Logging.js');
const validate = require('../tests/validate.js');

// Ensures validation passes, or exits
if (!validate()) {
  console.error('Some files failed to pass validation. Exiting.');
  process.exit(1);
}

// Print out startup time to default logs
Logging.printDefaultStatusMessage('Starting new instance of server.');
Logging.printErrorStatusMessage('Starting new instance of server.');

// Port that server will run on
const PORT = 8080;
// List of available file configurations
const SERVER_CONFIG = require('./json/server_config.json');

