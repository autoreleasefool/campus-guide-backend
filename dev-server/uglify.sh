#!/bin/bash

cp -r ../assets/ ../assets_min/

for filename in ../assets_min/config/*.json; do
  name=${filename##*/}
  echo "Uglify ../assets_min/config/$name -> ../assets_min/config/$name"
  uglifyjs "../assets_min/config/$name" --output "../assets_min/config/$name" -p expression -b beautify=false -b quote_style=2 -b quote_keys=true
done

for filename in ../assets_min/json/*.json; do
  name=${filename##*/}
  echo "Uglify ../assets_min/json/$name -> ../assets_min/json/$name"
  uglifyjs "../assets_min/json/$name" --output "../assets_min/json/$name" -p expression -b beautify=false -b quote_style=2 -b quote_keys=true
done
