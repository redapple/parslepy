#!/bin/bash

abort() {
    echo >&2 "$*"; exit 1;
}

usage() {
    abort """Usage: $(basename $0) OPTIONS
    -p|--port     Port number for the HTTP server to use (default: 8000)
    -b|--browser  Browser to open the link (default: xdg-open)"""
}

require() {
    type $1 >/dev/null 2>&1
}

port=8000
browser=xdg-open
while [ "${1#-}" != "$1" ]; do
    case "$1" in
        -h) usage;;
        -p|--port) [ -z "$2" ] && usage; port="$2"; shift;;
        -b|--browser) [ -z "$2" ] && usage; browser="$2"; shift;;
        *) usage;;
    esac
    shift
done

require when-changed || abort "Please install this first:   sudo pip install when-changed"
require "$browser" || abort "$browser is not available -- please specify another browser"

# compile the first time
make html

# open web-browser
$browser http://localhost:$port/html &

# run HTTP server in background inside the _build dir
# NOTE: here, cd also runs in bg, so the script's current dir stays the same
cd _build && python -m SimpleHTTPServer $port &

# watch for changes
when-changed index.rst -c "make html; echo Use Ctrl-C to quit preview"

