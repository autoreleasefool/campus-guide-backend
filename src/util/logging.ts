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
 * @file logging.js
 * @description Provides logging functions
 */

// Header/footer for status messages
const STATUS_MESSAGE_SEPARATOR = '----------------------------------------';

/**
 * Prints a message to the console with the current time and separators.
 *
 * @param {string} message the message to print
 * @param {function} log   the function to output with
 */
function printStatusMessage(message: string, log: (message: string) => void): void {
  log(STATUS_MESSAGE_SEPARATOR);
  const MAX_LINE_LENGTH = STATUS_MESSAGE_SEPARATOR.length;

  let currentLineLength = 0;
  let currentLine = '';
  const pieces = message.split(' ');
  for (const piece of pieces) {
    if (currentLineLength + piece.length < MAX_LINE_LENGTH) {
      currentLineLength += piece.length + 1;
      currentLine += `${piece} `;
    } else {
      log(currentLine);
      currentLineLength = 0;
      currentLine = '';
    }
  }

  if (currentLineLength > 0) {
    log(currentLine);
  }

  log((new Date()).toString());
  log(STATUS_MESSAGE_SEPARATOR);
}

/**
 * Prints a message to the error output with the current time and separators.
 *
 * @param {string} message the message to print
 */
export function printErrorStatusMessage(message: string): void {
  printStatusMessage(message, console.error);
}

/**
 * Prints a message to the standard output with the current time and separators.
 *
 * @param {string} message the message to print
 */
export function printDefaultStatusMessage(message: string): void {
  printStatusMessage(message, console.log);
}
