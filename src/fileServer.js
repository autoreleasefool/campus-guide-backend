
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
 * @file fileServer.js
 * @description Enables a static file server (for development purposes)
 *
 * @flow
 */
'use strict';

const express = require('express');
const path = require('path');

module.exports = (app: any) => {

  // Add charset=utf-8 to headers
  const options = {
    setHeaders: (res, file) => {
      if (file.endsWith('.json')) {
        res.set('Content-Type', 'application/json; charset=utf-8');
      }
    },
  };

  // Serve assets
  app.use('/assets', express.static(path.join(__dirname, 'assets'), options));

};
