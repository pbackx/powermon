from dotenv import load_dotenv
import json
import os
from sanic import Sanic
from sanic_ext import Extend
from sanic.log import logger
from sanic.response import json as sanic_json
import websockets

load_dotenv()
app = Sanic(__name__)
cors_origins = os.getenv("CORS_ORIGINS")
if cors_origins is not None:
    app.config.CORS_ORIGINS=cors_origins
Extend(app)

token = os.environ.get('SUPERVISOR_TOKEN')
if token is None:
    raise ValueError('SUPERVISOR_TOKEN environment variable not set')

websocket_url = os.environ.get('WEBSOCKET_URL', 'ws://supervisor/core/api/websocket')


@app.get("/")
def hello_world(request):
    return sanic_json({"message": "Hello, World!"})


async def homeassistant_connection():
    logger.info(f'Connecting to Home Assistant at {websocket_url}')
    async with websockets.connect(websocket_url) as websocket:
        r = await websocket.recv()
        rtype = json.loads(r)["type"]
        if rtype == "auth_required":
            logger.info("HA WS: auth_required")
            await websocket.send(json.dumps({"type": "auth", "access_token": token}))
            r = await websocket.recv()
            rtype = json.loads(r)["type"]
            if rtype == "auth_ok":
                logger.info("HA WS: auth_ok")
                await websocket.send(json.dumps({"id": 1, "type": "subscribe_events", "event_type": "state_changed"}))
                while True:
                    r = await websocket.recv()
                    rjson = json.loads(r)
                    rtype = rjson["type"]
                    if rtype == "result":
                        logger.info("HA WS: subscription result: {}".format(rjson["success"]))
                    elif rtype == "event":
                        rdata = rjson["event"]["data"]
                        if rdata["entity_id"] == "sensor.power_consumption":
                            logger.info(
                                f'HA WS: [{rdata["new_state"]["last_changed"]}] {rdata["new_state"]["state"]}{rdata["new_state"]["attributes"]["unit_of_measurement"]}')
                            # to test: check if firing an event for a nonexisting entity creates the entity
                            # https://developers.home-assistant.io/docs/api/websocket#fire-an-event
            else:
                logger.info("HA WS: auth_failed")
                return
        else:
            logger.info("HA WS: Unexpected message: ", r)
            return


app.add_task(homeassistant_connection())
