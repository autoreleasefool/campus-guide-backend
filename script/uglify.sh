#!/bin/bash

cp -r "$1/assets/" "$1/assets_min/"

for filename in $1/assets_min/config/*.json; do
  name=${filename##*/}
  echo "Uglify $1/assets_min/config/$name -> $1/assets_min/config/$name"
  uglifyjs "$1/assets_min/config/$name" --output "$1/assets_min/config/$name" -p expression -b beautify=false -b quote_style=2 -b quote_keys=true
  gzip -9 --keep "$1/assets_min/config/$name"
done

for filename in $1/assets_min/json/*.json; do
  name=${filename##*/}
  echo "Uglify $1/assets_min/json/$name -> $1/assets_min/json/$name"
  uglifyjs "$1/assets_min/json/$name" --output "$1/assets_min/json/$name" -p expression -b beautify=false -b quote_style=2 -b quote_keys=true
  gzip -9 --keep "$1/assets_min/json/$name"
done

for filename in $1/assets_min/images/*; do
  name=${filename##*/}
  echo "Zip $1/assets_min/images/$name -> $1/assets_min/images/$name"
  gzip -9 --keep "$1/assets_min/images/$name"
done
