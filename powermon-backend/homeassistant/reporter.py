import logging
import os
import random
from datetime import datetime, timedelta

import aiohttp
from apscheduler.schedulers.base import BaseScheduler

from powermon.database import PowermonDatabase
from powermon.utils import round_down_quarter


class Reporter:
    def __init__(self, ha_core_api_url, headers, scheduler: BaseScheduler, database: PowermonDatabase):
        self.ha_core_api_url = ha_core_api_url
        self.headers = headers
        self.scheduler = scheduler
        self.database = database

        self.scheduler.add_job(self.send_quarter_average_update, 'cron', second='*/15', minute='1,16,31,46')
        self.scheduler.add_job(self.send_month_peak_update, 'cron', day='1', hour='0', minute='1', second='0')

        self.shared_attribute = {"unit_of_measurement": "W",
                                 "device_class": "power",
                                 "state_class": "measurement"}

        self.power_average_out = os.environ.get('POWER_AVERAGE_OUT')
        if self.power_average_out is None:
            raise ValueError('POWER_AVERAGE_OUT environment variable not set')
        self.power_peak_out = os.environ.get('POWER_PEAK_OUT')
        if self.power_peak_out is None:
            raise ValueError('POWER_PEAK_OUT environment variable not set')

    async def send_quarter_average_update(self):
        logging.info('Sending quarter average to HA.')
        # TODO get actual value from database
        previous_quarter = round_down_quarter(datetime.now()) - timedelta(minutes=15)
        logging.info(f'Getting average for {previous_quarter}')
        await self.send_value_to_ha(self.power_average_out,
                                    random.Random().randint(200, 400),
                                    'Power Average of Previous 15 Minutes')

    async def send_month_peak_update(self):
        logging.info('Sending month peak to HA.')
        # TODO get actual value from database
        await self.send_value_to_ha(self.power_peak_out,
                                    random.Random().randint(200, 400),
                                    'Power Peak of Previous Month')

    async def send_value_to_ha(self, sensor: str, value: float, friendly_name):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f'{self.ha_core_api_url}/states/{sensor}',
                                    json={"state": value,
                                          "attributes": {
                                              **self.shared_attribute,
                                              "friendly_name": friendly_name,
                                          }}) as resp:
                if resp.status != 200:
                    logging.error(f'Error updating power average sensor: {resp.status}, {await resp.text()}')
