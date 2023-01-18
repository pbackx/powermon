import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from aiohttp import web
import aiohttp
from aiohttp_middlewares import cors_middleware
from dotenv import load_dotenv

from powermon.database import PowermonDatabase
from powermon.model import PowerReading, PowerUpdate

load_dotenv()
token = os.environ.get('SUPERVISOR_TOKEN')
if token is None:
    raise ValueError('SUPERVISOR_TOKEN environment variable not set')
headers = {'Authorization': f'Bearer {token}'}

websocket_url = os.environ.get('WEBSOCKET_URL', 'ws://supervisor/core/api/websocket')
ha_core_api_url = os.environ.get('HA_CORE_API_URL', 'http://supervisor/core/api')
supervisor_api_url = 'http://supervisor'

power_sensor = os.environ.get('POWER_SENSOR')
if power_sensor is None:
    raise ValueError('POWER_SENSOR environment variable not set')

database = PowermonDatabase(os.environ.get('DATABASE_FILE', '/data/powermon.db'))
local_timezone = datetime.now(timezone.utc).astimezone().tzinfo


async def hello_world(request):
    return web.json_response({"message": "Hello, World!"})


async def get_power_sensor(request):
    return web.json_response({"selected_sensor": power_sensor})


async def update_power_sensor(request):
    global power_sensor
    data = await request.json()
    new_sensor = data['selected_sensor']
    logging.info(f'Updating power sensor to {new_sensor}')
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f'{supervisor_api_url}/addons/self/options',
                                    json={"options": {"power_sensor": new_sensor}}) as resp:
                if resp.status == 200:
                    logging.info(f'Power sensor updated to {new_sensor}')
                    power_sensor = new_sensor
                    return web.json_response({"selected_sensor": new_sensor})
                else:
                    logging.error(f'Error updating power sensor: {resp.status}, {await resp.text()}')
                    return web.json_response({"selected_sensor": power_sensor})
    except aiohttp.ClientConnectionError as e:
        logging.error(f'Error updating power sensor: {e}')
        return web.json_response({"selected_sensor": power_sensor}, status=400)


async def load_power_sensors(request):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'{ha_core_api_url}/states') as resp:
            sensors = await resp.json()
            power_sensors = [sensor for sensor in sensors if
                             sensor['attributes'].get('device_class') is not None
                             and sensor['attributes']['device_class'] == 'power']
            return web.json_response(power_sensors)


async def delete_database(request):
    database.delete_data()
    return web.json_response({"message": "Database deleted"})


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app['websockets'].append(ws)

    readings = database.get_power_readings(datetime.now(local_timezone) - timedelta(hours=1),
                                           datetime.now(local_timezone))
    await ws.send_json([PowerUpdate(reading.power, reading.timestamp, 'reading').to_json() for reading in readings])

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
                request.app['websockets'].remove(ws)
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.warning('ws connection closed with exception %s' %
                            ws.exception())

    logging.warning('websocket connection closed')

    return ws


async def homeassistant_listener(app):
    logging.info(f'Connecting to Home Assistant at {websocket_url}')
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(websocket_url) as websocket:
            async for msg in websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                        await websocket.close()
                    else:
                        rjson = json.loads(msg.data)
                        rtype = rjson["type"]
                        if rtype == "auth_required":
                            await websocket.send_json({"type": "auth", "access_token": token})
                        elif rtype == "auth_ok":
                            logging.info('Successfully authenticated with Home Assistant')
                            await websocket.send_json(
                                {"id": 1, "type": "subscribe_events", "event_type": "state_changed"})
                        elif rtype == "result":
                            logging.info("HA WS: subscription result: {}".format(rjson["success"]))
                        elif rtype == "event":
                            rdata = rjson["event"]["data"]
                            if rdata["entity_id"] == power_sensor:
                                reading = PowerReading(
                                    rdata["new_state"]["state"],
                                    rdata["new_state"]["last_changed"],
                                    rdata["new_state"]["attributes"]["unit_of_measurement"])
                                logging.info(f'HA WS: {reading}')
                                updates = database.insert_power_reading(reading)
                                for ws in app['websockets']:
                                    try:
                                        await ws.send_json([update.to_json() for update in updates])
                                    except Exception as e:
                                        logging.error(f'Error sending to websocket: {e}')
                                        app['websockets'].remove(ws)


async def homeassistant_connection(app):
    app['homeassistant_listener'] = asyncio.create_task(homeassistant_listener(app))
    yield
    app['homeassistant_listener'].cancel()
    await app['homeassistant_listener']


def init_func():
    middlewares = []

    cors_origins = os.getenv("CORS_ORIGINS")
    if cors_origins:
        middlewares.append(
            cors_middleware(
                origins=cors_origins.split(","),
            )
        )

    app = web.Application(middlewares=middlewares)
    app.add_routes([
        web.get('/', hello_world),
        web.get('/sensor', get_power_sensor),
        web.post('/sensor', update_power_sensor),
        web.get('/sensor/list', load_power_sensors),
        web.delete('/database', delete_database),
        web.get('/ws', websocket_handler)
    ])

    app['websockets'] = []
    app.cleanup_ctx.append(homeassistant_connection)

    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web.run_app(init_func(), port=8000, host='0.0.0.0')
