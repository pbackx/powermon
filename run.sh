#!/usr/bin/with-contenv bashio

POWER_SENSOR="$(bashio::config 'power_sensor')"
export POWER_SENSOR
POWER_AVERAGE_OUT="$(bashio::config 'power_average_out')"
export POWER_AVERAGE_OUT
POWER_PEAK_OUT="$(bashio::config 'power_peak_out')"
export POWER_PEAK_OUT

cd /backend || exit
python3 main.py &

cd /frontend || exit
nginx -g "daemon off;error_log /dev/stdout debug;"
