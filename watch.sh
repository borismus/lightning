#!/usr/bin/env sh

SOURCE_PATH=./content

while true; do
  inotifywait -r $SOURCE_PATH -e close_write -e create -e delete -e moved_from;
  python engine/parser.py
done

