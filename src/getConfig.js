
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
 * @file getConfig.js
 * @description GET request to get current config file versions for a version of the app
 *
 * @flow
 */
'use strict';

// Imports
const cron = require('cron');
const fs = require('fs');
const http = require('http');
const path = require('path');
const Promise = require('promise');
const url = require('url');

// Environment variables
let serverEnv: Object = null;
// Contents of the serverConfig file
let serverConfig: Object = {};
// Time that the serverConfig file was last updated
let serverConfigLastModified: number = 0;

/**
 * Iterates over each file in the configuration and ensures their filenames are unique.
 *
 * @returns {Promise<void>} promise that resolves if all configuration names are unique, or rejects otherwise
 */
function validateConfigNames(): Promise < void > {
  return new Promise((resolve, reject) => {
    const configNames: Object = {};
    for (let i = 0; i < serverConfig.length; i++) {
      if (serverConfig[i].name in configNames) {
        reject('Duplicate configuration filenames: ' + serverConfig[i].name);
        return;
      } else {
        configNames[serverConfig[i].name] = true;
      }
    }

    resolve();
  });
}

/**
 * Iterates over config files and gets the file size of each
 *
 * @returns {Promise<void>} promise that resolves when the size of config files are all updated
 */
function refreshConfigSizes(): Promise < void > {
  return new Promise(resolve => {
    let versionSizesReceived: number = 0;

    const requestSizeReceived = () => {
      versionSizesReceived += 1;
      if (versionSizesReceived === totalVersions) {
        resolve();
      }
    };

    // Get the total number of files for which sizes must be retrieved.
    let totalVersions: number = 0;
    for (let i = 0; i < serverConfig.length; i++) {
      for (const version in serverConfig[i].versions) {
        if (serverConfig[i].versions.hasOwnProperty(version)) {
          totalVersions++;
        }
      }
    }

    // Get the new size from headers of each version file
    for (let i = 0; i < serverConfig.length; i++) {
      for (const version in serverConfig[i].versions) {
        if (serverConfig[i].versions.hasOwnProperty(version)) {
          const fileVersion = serverConfig[i].versions[version];
          const fileURL = url.parse(fileVersion.location.url);
          const options = {
            method: 'HEAD',
            hostname: fileURL.hostname,
            port: fileURL.port,
            path: fileURL.path,
          };

          const req = http.request(options, res => {
            fileVersion.size = parseInt(res.headers['content-length']);
            requestSizeReceived();
          });

          req.end();
        }
      }
    }
  });
}

// Run a cron job once an hour to ensure configuration in memory is the most recent available.
const updateConfigCronJob = new cron.CronJob({
  cronTime: '0 0 * * * *',
  onTick: () => {
    console.log('Running updateConfigCronJob on ' + (new Date()));

    fs.stat(path.join(__dirname, 'json', 'server_config.json'), (statErr, stats) => {
      if (statErr) {
        // Check for error
        console.error('Error opening server_config.json', statErr);
        return;
      }

      // Check if the file has been updated since it was last checked and if so, update it
      if (stats.mtime.getTime() !== serverConfigLastModified) {
        fs.readFile(path.join(__dirname, 'json', 'server_config.json'), 'utf8', (readErr, data) => {
          if (readErr) {
            // Check for error
            console.error('Error opening server_config.json', readErr);
            return;
          }

          // Get a copy of the config just in case an error occurs
          const savedConfig = JSON.parse(JSON.stringify(serverConfig));

          // Update config file and modified time
          serverConfig = serverEnv.replaceConfigUrls(JSON.parse(data), false);
          validateConfigNames()
              .then(refreshConfigSizes)
              .then(() => {
                console.log('Server configuration updated on ' + (new Date()));
                serverConfigLastModified = stats.mtime.getTime();
              })
              .catch(err => {
                console.error('Error encountered while updating config. Reverting configuration.', err);
                serverConfig = savedConfig;
              });
        });
      }
    });
  },
  start: false,
  timeZone: 'America/Los_Angeles',
});
updateConfigCronJob._callbacks[0]();
updateConfigCronJob.start();

module.exports = (app, env) => {

  // Save the environment variables
  serverEnv = env;

  // Endpoint for retrieving config for a version of the app
  app.get('/config/:version', (req, res) => {

    // Get client version of the application
    const appVersion = req.params.version.trim();

    // Load JSON data, prepare data to send back to user
    const appConfig: Object = {};

    for (let i = 0; i < serverConfig.length; i++) {
      const configFile: Object = serverConfig[i];

      // If the file is available for the app version, send the file's most recent version
      if (appVersion in configFile.versions) {
        appConfig[configFile.name] = configFile.versions[appVersion];
        appConfig[configFile.name].type = configFile.type;
      }
    }

    res.json(appConfig);
  });
};
