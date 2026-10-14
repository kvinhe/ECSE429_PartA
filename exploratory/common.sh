#!/bin/bash
# Shared helper: echo each curl command, then status code and (trimmed) body.
BASE=${TODO_API_URL:-http://localhost:4567}
JSON='Content-Type: application/json'
XML='Content-Type: application/xml'
call() {  # call METHOD PATH [curl args...]
  local method=$1 path=$2; shift 2
  echo "\$ curl -X $method $BASE$path $*"
  curl -s -m 10 -X "$method" "$BASE$path" "$@" -w '\n  -> HTTP %{http_code}\n' | cut -c1-300
}
