#!/bin/bash

for filename in ./src/assets/json/*.json; do
  name=${filename##*/}
  echo "Uglify ./src/assets/json/$name -> ./build/assets/json/$name"
  uglifyjs "./src/assets/json/$name" --output "./build/assets/json/$name" --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
done
