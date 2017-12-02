# Campus Guide - Backend

[![Build status](https://travis-ci.org/josephroque/campus-guide-backend.svg?branch=master)](https://travis-ci.org/josephroque/campus-guide-backend)

Backend configuration management for the Campus Guide mobile app.

## Description

Provides scripts to manage assets for the Campus Guide mobile app, including:
- Automated upload to S3 of new assets
- Version metadata management for assets which have changed
- Automated builds of configuration files
- A local development server so you can still test the app offline

## How to use

[Optional - set up environment]

```
mkvirtualenv campusguide
workon campusguide
pip install -r requirements.txt
```

To start a dev-server for development:

```
cd dev-server
yarn start
```

To quickly upload assets to a release AWS bucket:

```
./script/release_manager.py BUCKET_NAME assets/ assets_release/ <major/minor/patch>
```

For further options:

```
./script/release_manager.py
```
