import asyncio
import json
import logging
import os

from aiohttp import web
import aiohttp
from aiohttp_middlewares import cors_middleware
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get('SUPERVISOR_TOKEN')
if token is None:
    raise ValueError('SUPERVISOR_TOKEN environment variable not set')

websocket_url = os.environ.get('WEBSOCKET_URL', 'ws://supervisor/core/api/websocket')


async def hello_world(request):
    return web.json_response({"message": "Hello, World!"})


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app['websockets'].append(ws)

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
                            if rdata["entity_id"] == "sensor.power_consumption":
                                logging.info(
                                    f'HA WS: [{rdata["new_state"]["last_changed"]}] {rdata["new_state"]["state"]}{rdata["new_state"]["attributes"]["unit_of_measurement"]}')
                                for ws in app['websockets']:
                                    try:
                                        await ws.send_json(rdata["new_state"])
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
        web.get('/ws', websocket_handler)
    ])

    app['websockets'] = []
    app.cleanup_ctx.append(homeassistant_connection)

    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web.run_app(init_func(), port=8000, host='0.0.0.0')
