
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
 * @file getConfig.ts
 * @description GET request to get current config file versions for a version of the app
 */
'use strict';

/** Versioning for config files. */
interface ConfigFileVersion {
  location: { url: string };
  size?: number;
  type?: string;
  version: number;
}

/** Config files to send to app. */
interface ConfigFile {
  name: string;
  type: string;
  versions: {
    [key: string]: ConfigFileVersion;
  };
}

/** Server configuration to manage files. */
interface ServerConfig {
  lastUpdatedAt: number;
  files: ConfigFile[];
}

// Imports
import * as express from 'express';
import * as HttpStatus from 'http-status-codes';
import * as request from 'request-promise-native';

// Contents of the serverConfig file
let serverConfig: ServerConfig;

/**
 * Iterates over each file in the configuration and ensures their filenames are unique.
 *
 * @param {ServerConfig} config the server configuration to validate
 * @returns {Promise<void>} promise that resolves if all configuration names are unique, or rejects otherwise
 */
async function validateConfigNames(config: ServerConfig): Promise<void> {
  const configNames = new Set();

  for (const file of config.files) {
    if (configNames.has(file.name)) {
      throw new Error(`Duplication configuration filenames: ${file.name}`);
    } else {
      configNames.add(file.name);
    }
  }
}

/**
 * Refreshes the server configuration file.
 *
 * @param {any} env environment variables
 */
async function refreshConfig(env: any): Promise<void> {

  // Get a copy of the config just in case an error occurs
  const savedConfig = JSON.parse(JSON.stringify(serverConfig || {}));

  const runDate = new Date();
  console.log(`Force refreshing configuration on ${runDate.toString()}`);

  const uri = `${env.fileServer}/assets/config.json`;
  const options = {
    json: true,
    method: 'GET',
    uri,
  };

  try {
    const freshConfig = await request(options);
    if (!serverConfig || freshConfig.lastUpdatedAt > (serverConfig.lastUpdatedAt || 0)) {
      // Update config file and modified time
      replaceConfigUrls(env, freshConfig);
      await validateConfigNames(freshConfig);
      await refreshConfigSizes(freshConfig);
      serverConfig = freshConfig;
      console.log(`Server configuration updated on ${(new Date()).toString()}`);
    }
  } catch (err) {
    console.error('Failed to updated configuration.', err);
    serverConfig = savedConfig;
    throw err;
  }
}

/**
 * Replaces configuration substrings recursively in the object.
 *
 * @param {any}          env    private environment variables
 * @param {ServerConfig} config the object to recursively update
 * @param {boolean}      clone  false to alter the original object, true to clone
 * @returns {ServerConfig} the updated config
 */
function replaceConfigUrls(env: any, config: ServerConfig): ServerConfig {
  for (const key in config) {
    if (config.hasOwnProperty(key)) {
      const value = config[key];
      if (typeof (value) === 'string') {
        config[key] = value.replace('{file_server}', env.fileServer);
      } else if (typeof (value) === 'object') {
        config[key] = replaceConfigUrls(env, config[key]);
      }
    }
  }

  return config;
}

/**
 * Iterates over config files and gets the file size of each
 *
 * @param {ServerConfig} config the configuration for files
 * @returns {Promise<void>} promise that resolves when the size of config files are all updated
 */
async function refreshConfigSizes(config: ServerConfig): Promise<void> {
  // Get the new size from headers of each version file
  for (const file of config.files) {
    for (const version in file.versions) {
      if (file.versions.hasOwnProperty(version)) {
        const fileVersion = file.versions[version];
        const options = {
          method: 'HEAD',
          uri: fileVersion.location.url,
        };

        try {
          const response = await request(options);
          fileVersion.size = parseInt(response['content-length'] as string);
        } catch (err) {
          console.error(`Failed to retrieve config file headers: ${file.name}`, err);
        }
      }
    }
  }
}

export function setup(app: express.Application, env: any): void {

  // Endpoint to force refresh config versions
  app.get('/config/refresh', async(_: express.Request, res: express.Response) => {
    try {
      await refreshConfig(env);
      res.sendStatus(HttpStatus.OK);
    } catch (err) {
      console.error(err);
      res.sendStatus(HttpStatus.INTERNAL_SERVER_ERROR);
    }
  });

  // Endpoint for retrieving config for a version of the app
  app.get('/config/:version', (req: express.Request, res: express.Response) => {

    // Get client version of the application
    const appVersion = req.params.version.trim();

    // Load JSON data, prepare data to send back to user
    const appConfig: { [name: string]: ConfigFileVersion } = {};

    for (const file of serverConfig.files) {
      // If the file is available for the app version, send the file's most recent version
      if (appVersion in file.versions) {
        appConfig[file.name] = file.versions[appVersion];
        appConfig[file.name].type = file.type;
      } else if ('*' in file.versions) {
        appConfig[file.name] = file.versions['*'];
        appConfig[file.name].type = file.type;
      }
    }

    res.json(appConfig);
  });

}
