#!/usr/bin/with-contenv bashio

cd /backend || exit
python3 powermon.py &

cd /frontend || exit
nginx -g "daemon off;error_log /dev/stdout debug;"
