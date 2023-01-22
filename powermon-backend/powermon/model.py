from datetime import datetime
from enum import Enum


class PowerReading:
    def __init__(self, power, timestamp=datetime.now(), unit_of_measurement='W'):
        if isinstance(power, str):
            power = float(power)
        if unit_of_measurement == 'kW':
            self.power = power * 1000
        else:
            self.power = power

        if isinstance(timestamp, str):
            self.timestamp = datetime.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp

    def __str__(self):
        return f'[{self.timestamp}] {self.power}W'

    def to_json(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'power': self.power
        }


class PowerUpdateType(Enum):
    READING = 'reading'
    AVERAGE = 'average'
    PEAK = 'peak'
    YEAR_AVERAGE = 'year_average'


class PowerUpdate:
    def __init__(self, power, timestamp, update_type):
        self.power = power
        if isinstance(timestamp, str):
            self.timestamp = datetime.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp
        self.type = PowerUpdateType(update_type)

    def __str__(self):
        return f'[{self.timestamp}] {self.power}W {self.type.value}'

    def to_json(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'power': self.power,
            'type': self.type.value
        }


class PowerEvent:
    #TODO add actual data
    def __init__(self):
        self.id = 0

    def to_json(self):
        self.id += 1
        return {
            'id': self.id,
            'type': 'fire_event',
            'event_type': 'state_changed',
            'event_data': {
                'entity_id': 'sensor.powermon_power_average',
                'state': 500,
                'attributes': {
                    'unit_of_measurement': 'W',
                    'friendly_name': 'Powermon Power Average',
                    'device_class': 'power',
                    'state_class': 'measurement'
                }
            }
        }
