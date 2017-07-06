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

// Defines the required defined environment variables
export interface Environment {
  authKey: string;
  enableFileServer: boolean;
  fileServer: string;
}

// Imports
import * as envDefaults from './defaults';
import * as express from 'express';
import * as fileServer from './fileServer';
import * as HttpStatus from 'http-status-codes';
import * as configRoutes from './getConfig';
import * as logging from './util/logging';
import * as validator from './util/validator';

const env: Environment = {
  authKey: process.env.NODE_ENV === 'production' && process.env.AUTH_KEY
      ? process.env.AUTH_KEY : envDefaults.authKey,
  enableFileServer: process.env.ENABLE_FILE_SERVER === 'true' || envDefaults.enableFileServer,
  fileServer: process.env.NODE_ENV === 'production' && process.env.FILE_SERVER
      ? process.env.FILE_SERVER : envDefaults.fileServer,
};

console.log(env);

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

if (process.env.NODE_ENV !== 'production') {
  console.log('WARNING! You haven\'t enabled a production environment for this instance!');
} else if (env.authKey === envDefaults.authKey) {
  console.error('ERROR! You haven\'t set a custom authorization key for this instance.');
  throw new Error('Authorization key cannot be default in production. Ensure you provide AUTH_KEY env variable.');
}

// Create server
const app = express();

// Log each request made to the server and confirm the auth key
app.use((req: express.Request, res: express.Response, next: any) => {
  const date = new Date();

  const auth = req.header('Authorization');
  if (auth !== env.authKey) {
    console.log(`Unauthorized access! (${date.toString()} -- ${req.ip}) ${req.method}: ${req.originalUrl} -- ${auth}`);
    res.sendStatus(HttpStatus.UNAUTHORIZED);
  } else {
    console.log(`(${date.toString()} -- ${req.ip}) ${req.method}: ${req.originalUrl}`);
    next();
  }
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
