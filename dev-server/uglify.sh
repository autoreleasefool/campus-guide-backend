#!/bin/bash

mkdir -p ./build/assets/json

for filename in ../assets/json/*.json; do
  name=${filename##*/}
  echo "Uglify ../assets/json/$name -> ./build/assets/json/$name"
  uglifyjs "../assets/json/$name" --output "./build/assets/json/$name" -p expression -b beautify=false -b quote_style=2 -b quote_keys=true
done
