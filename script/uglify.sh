#!/bin/bash

# Given a directory of assets ($1), copy the assets to a new directory ($2) and minify the
# copied assets in place

cp -r "$1" "$2"

for filename in $2json/*.json; do
  name=${filename##*/}
  echo "Uglify $2json/$name"
  uglifyjs "$2json/$name" --output "$2json/$name" -p expression -b beautify=false -b quote_style=2 -b quote_keys=true
  gzip -9 --keep "$2json/$name"
done

for filename in $2images/*; do
  name=${filename##*/}
  echo "Zip $2images/$name"
  gzip -9 --keep "$2images/$name"
done

for filename in $2text/*; do
  name=${filename##*/}
  echo "Zip $2text/$name"
  gzip -9 --keep "$2text/$name"
done
