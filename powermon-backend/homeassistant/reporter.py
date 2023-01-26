import logging
import os
from datetime import datetime

import aiohttp

from powermon.model import PowerUpdateType
from powermon.utils import round_down_quarter


class Reporter:
    def __init__(self, ha_core_api_url, headers):
        self.ha_core_api_url = ha_core_api_url
        self.headers = headers

        self.last_update = round_down_quarter(datetime.now())
        self.last_update_average = None
        self.last_update_peak = None

        self.shared_attribute = {"unit_of_measurement": "W",
                                 "device_class": "power",
                                 "state_class": "measurement"}

        self.power_average_out = os.environ.get('POWER_AVERAGE_OUT')
        if self.power_average_out is None:
            raise ValueError('POWER_AVERAGE_OUT environment variable not set')
        self.power_peak_out = os.environ.get('POWER_PEAK_OUT')
        if self.power_peak_out is None:
            raise ValueError('POWER_PEAK_OUT environment variable not set')

    def store_updates(self, updates):
        updates_average = [update for update in updates if update.type == PowerUpdateType.AVERAGE]
        self.last_update_average = updates_average[-1] if len(updates_average) > 0 else None
        updates_peak = [update for update in updates if update.type == PowerUpdateType.PEAK]
        self.last_update_peak = updates_peak[-1] if len(updates_peak) > 0 else None

    async def send_quarterly_update(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            if self.last_update_average is not None:
                async with session.post(f'{self.ha_core_api_url}/states/{self.power_average_out}',
                                        json={"state": self.last_update_average.power,
                                              "attributes": {
                                                  **self.shared_attribute,
                                                  "friendly_name": "Power Average of Previous 15 Minutes",
                                              }}) as resp:
                    if resp.status != 200:
                        logging.error(f'Error updating power average sensor: {resp.status}, {await resp.text()}')
            if self.last_update_peak is not None:
                async with session.post(f'{self.ha_core_api_url}/states/{self.power_peak_out}',
                                        json={"state": self.last_update_peak.power,
                                              "attributes": {
                                                  **self.shared_attribute,
                                                  "friendly_name": "Power Peak of Previous Month (highest 15 minutes)",
                                              }}) as resp:
                    if resp.status != 200:
                        logging.error(f'Error updating power peak sensor: {resp.status}, {await resp.text()}')

    async def send_updates(self, updates):
        self.store_updates(updates)

        # TODO probably best to just use a timer to send updates every 15 minutes
        current_quarter = round_down_quarter(datetime.now())
        if current_quarter != self.last_update:
            self.last_update = current_quarter
            await self.send_quarterly_update()
