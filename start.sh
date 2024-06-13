#!/bin/sh
set -e

sleep 3 # Sleep 3 seconds for railway private url to init

uvicorn app.main:app --host "0.0.0.0" --port $PORT