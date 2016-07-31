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
const env = require('./env.js');
const express = require('express');
const logging = require('./utils/logging.js');
const validate = require('./tests/validate.js');

// Ensures validation passes, or exits
logging.printDefaultStatusMessage('Starting validation.');
if (!validate()) {
  console.error('Some files failed to pass validation. Exiting.');
  logging.printDefaultStatusMessage('Validation was unsuccessful. Check error logs.');
  process.exit(1);
}
logging.printDefaultStatusMessage('Validation successful.');

// Print out startup time to default logs
logging.printDefaultStatusMessage('Starting new instance of server.');
logging.printErrorStatusMessage('Starting new instance of server.');

// Port that server will run on
const PORT: number = 8080;

// Create server
const app = express();

// Enable file server (for development)
if (env.enableFileServer) {
  require('./fileServer.js')(app, env);
}

// Enable config checks
require('./getConfig.js')(app, env);

const server = app.listen(PORT, () => {

  const host = server.address().address;
  const port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});
