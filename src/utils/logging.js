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
 * @file Logging.js
 * @description Provides logging functions
 *
 * @flow
 */
'use strict';

// Header/footer for status messages
const STATUS_MESSAGE_SEPARATOR: string = '----------------------------------------';

module.exports = {

  /**
   * Prints a message to the console with the current time and separators.
   *
   * @param {string} message the message to print
   * @param {function} log   the function to output with
   */
  printStatusMessage(message: string, log: () => any): void {
    log(STATUS_MESSAGE_SEPARATOR);
    const MAX_LINE_LENGTH = STATUS_MESSAGE_SEPARATOR.length;

    let currentLineLength: number = 0;
    let currentLine: string = '';
    const pieces: Array< string > = message.split(' ');
    for (let i = 0; i < pieces.length; i++) {
      if (currentLineLength + pieces[i].length < MAX_LINE_LENGTH) {
        currentLineLength += pieces[i].length + 1;
        currentLine += pieces[i] + ' ';
      } else {
        log(currentLine);
        currentLineLength = 0;
        currentLine = '';
      }
    }

    if (currentLineLength > 0) {
      log(currentLine);
    }

    log(new Date());
    log(STATUS_MESSAGE_SEPARATOR);
  },

  /**
   * Prints a message to the error output with the current time and separators.
   *
   * @param {string} message the message to print
   */
  printErrorStatusMessage(message: string): void {
    this.printStatusMessage(message, console.error);
  },

  /**
   * Prints a message to the standard output with the current time and separators.
   *
   * @param {string} message the message to print
   */
  printDefaultStatusMessage(message: string): void {
    this.printStatusMessage(message, console.log);
  },

};
