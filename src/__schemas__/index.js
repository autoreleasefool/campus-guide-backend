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
 * @file index.js
 * @description Exports all files in this directory
 *
 * @flow
 */
'use strict';

module.exports = [
  {
    name: '/details',
    schema: require('./details.schema.json'),
  },
  {
    name: '/icon',
    schema: require('./icon.schema.json'),
  },
  {
    name: '/link',
    schema: require('./link.schema.json'),
  },
  {
    name: '/section',
    schema: require('./section.schema.json'),
  },
];
