import logging
import os
import pprint
from datetime import datetime, timedelta

import aiohttp
from apscheduler.schedulers.base import BaseScheduler

from powermon.database import PowermonDatabase
from powermon.utils import round_down_quarter


class Reporter:
    def __init__(self, ha_core_api_url, headers, scheduler: BaseScheduler, database: PowermonDatabase, local_timezone):
        self.ha_core_api_url = ha_core_api_url
        self.headers = headers
        self.scheduler = scheduler
        self.database = database
        self.local_timezone = local_timezone

        self.scheduler.add_job(self.send_quarter_average_update, 'cron', minute='1,16,31,46')
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
        previous_quarter = round_down_quarter(datetime.now(self.local_timezone)) - timedelta(minutes=15)
        power_averages = self.database.get_power_averages(previous_quarter, previous_quarter + timedelta(minutes=5))
        if len(power_averages) != 0:
            await self.send_value_to_ha(self.power_average_out,
                                        power_averages[0].power,
                                        'Power Average of Previous 15 Minutes')
        else:
            logging.warning('No power average found for previous 15 minutes')

    async def send_month_peak_update(self):
        logging.info('Sending month peak to HA.')
        current_month_number = datetime.now(self.local_timezone).month
        previous_month_number = current_month_number - 1 if current_month_number > 1 else 12
        previous_month = datetime(year=datetime.now(self.local_timezone).year,
                                  month=previous_month_number,
                                  day=1,
                                  tzinfo=self.local_timezone)
        power_peaks = self.database.get_month_peaks(previous_month, previous_month + timedelta(days=1))
        if len(power_peaks) != 0:
            await self.send_value_to_ha(self.power_peak_out,
                                        power_peaks[0].power,
                                        'Power Peak of Previous Month')
        else:
            logging.warning('No power peak found for previous month')

    async def send_value_to_ha(self, sensor: str, value: float, friendly_name):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            body = {"state": value,
                    "attributes": {
                        **self.shared_attribute,
                        "friendly_name": friendly_name,
                    }}
            pp = pprint.PrettyPrinter(depth=4)
            logging.info(f'Updating sensor {sensor} with {pp.pformat(body)}')
            async with session.post(f'{self.ha_core_api_url}/states/{sensor}',
                                    json=body) as resp:
                if resp.status != 200 and resp.status != 201:
                    logging.error(f'Error updating power average sensor: {resp.status}, {await resp.text()}')
