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
 * @file server.ts
 * @description Provides main server functionality and routing.
 */

declare var process: any;

// Imports
import * as env from './env';
import * as express from 'express';
import * as fileServer from './fileServer';
import * as configRoutes from './getConfig';
import * as logging from './util/logging';
import * as validator from './util/validator';

// Ensures validation passes, or exits
logging.printDefaultStatusMessage('Starting validation.');
if (!validator.validate()) {
  logging.printErrorStatusMessage('Some files failed to pass validation. Exiting.');
  logging.printDefaultStatusMessage('Validation was unsuccessful. Check error logs.');
  process.exit(1);
}

logging.printDefaultStatusMessage('Validation successful.');

// Print out startup time to default logs
logging.printDefaultStatusMessage('Starting new instance of server.');
logging.printErrorStatusMessage('Starting new instance of server.');

// Create server
const app = express();

// Log each request made to the server
app.use((req: express.Request, _: express.Response, next: any) => {
  const date = new Date();
  console.log(`(${date.toString()} -- ${req.ip}) ${req.method}: ${req.originalUrl}`);
  next();
});

// Enable file server (for development)
if (env.enableFileServer) {
  fileServer.start(app);
}

// Enable config checks
configRoutes.setup(app, env);

// Port that server will run on
const PORT = 8080;

const server = app.listen(PORT, '127.0.0.1', () => {
  const host = server.address().address;
  const port = server.address().port;
  console.log('Campus Guide server listening at http://%s:%s', host, port);
});
