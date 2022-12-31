#!/usr/bin/with-contenv bashio
#CONFIG_PATH=/data/options.json
#LIQUOR="$(bashio::config 'liquor')"
#
#echo "Hello world! I like $LIQUOR"
#
#curl -X GET -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" -H "Content-Type: application/json" http://supervisor/core/api/config

cd /backend || exit
flask --app hello run -p 9000 --host=0.0.0.0 &

cd /frontend || exit
nginx -g "daemon off;error_log /dev/stdout debug;"
