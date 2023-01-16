from datetime import datetime


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
