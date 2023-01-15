#!/usr/bin/with-contenv bashio

POWER_SENSOR="$(bashio::config 'power_sensor')"
export POWER_SENSOR

cd /backend || exit
python3 main.py &

cd /frontend || exit
nginx -g "daemon off;error_log /dev/stdout debug;"
