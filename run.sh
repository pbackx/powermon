#!/usr/bin/with-contenv bashio

cd /backend || exit
waitress-serve --port 9000 --host=0.0.0.0 powermon:app &

cd /frontend || exit
nginx -g "daemon off;error_log /dev/stdout debug;"
