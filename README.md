# Campus Guide - Server

[![Build status](https://travis-ci.org/josephroque/campus-guide-server.svg?branch=master)](https://travis-ci.org/josephroque/campus-guide-server)
[![Dependency Status](https://david-dm.org/josephroque/campus-guide-server.svg)](https://david-dm.org/josephroque/campus-guide-server)
[![devDependency Status](https://david-dm.org/josephroque/campus-guide-server/dev-status.svg)](https://david-dm.org/josephroque/campus-guide-server?type=dev)

A Node.js backend that directs the Campus Guide application to various configuration files.

## How to Deploy

In a non-production environment, the Authorization key for the server is loaded from 'src/defaults.ts'. To deploy an instance in production, you must provide the environment variable NODE_ENV = 'production', as well as a non-default AUTH\_KEY environment variable value.

Example command: `NODE_ENV=production AUTH\_KEY=NON\_DEFAULT\_KEY yarn start`
