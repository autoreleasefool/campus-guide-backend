/**
 * @license
 * Copyright (C) 2017 Joseph Roque
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
 * @description Development server for testing.
 */

// Imports
const express = require('express');
const path = require('path');

// Create server
const app = express();

// Log each request made to the server
app.use((req, res, next) => {
  const date = new Date();
  console.log(`(${date.toString()} -- ${req.ip}) ${req.method}: ${req.originalUrl}`);
  next();
});

// Add charset=utf-8 to headers
const options = {
  setHeaders: (res, file) => {
    if (file.endsWith('.json')) {
      res.set('Content-Type', 'application/json; charset=utf-8');
    }
  },
};

// Serve assets
app.use('/assets', express.static(path.join(__dirname, 'build', 'assets'), options));

// Port that server will run on
const PORT = 8080;

const server = app.listen(PORT, '127.0.0.1', () => {
  const host = server.address().address;
  const port = server.address().port;
  console.log('Campus Guide Dev Server listening at http://%s:%s', host, port);
});
