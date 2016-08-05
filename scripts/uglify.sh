#!/bin/bash

uglifyjs ./src/assets/json/app_config.json --output ./build/assets/json/app_config.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/course_formats.json --output ./build/assets/json/course_formats.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/disciplines.json --output ./build/assets/json/disciplines.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/faculties.json --output ./build/assets/json/faculties.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/room_types.json --output ./build/assets/json/room_types.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/settings.json --output ./build/assets/json/settings.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/transit_stops.json --output ./build/assets/json/transit_stops.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
uglifyjs ./src/assets/json/transit_times.json --output ./build/assets/json/transit_times.json --expr -b beautify=false -b keep_quoted_props=true -b quote-keys=true
