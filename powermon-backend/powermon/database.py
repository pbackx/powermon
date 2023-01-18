import sqlite3
from datetime import datetime

from .model import PowerReading, PowerUpdate
from .utils import round_down_quarter, beginning_of_month


class PowermonDatabase:
    def __init__(self, database_file):
        self.db = None
        self.db_file = database_file
        self.create_db()

    def create_db(self):
        self.db = sqlite3.connect(self.db_file)
        self.db.execute('CREATE TABLE IF NOT EXISTS power (timestamp DATETIME, power REAL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS power_quarter_average '
                        '(timestamp DATETIME, power_average REAL, num_readings INTEGER)')
        self.db.execute('CREATE TABLE IF NOT EXISTS power_month_peak'
                        '(timestamp DATETIME PRIMARY KEY, power_peak REAL)')
        self.db.commit()

    def insert_power_reading(self, reading: PowerReading):
        self.db.execute('INSERT INTO power VALUES (?, ?)', (reading.timestamp, reading.power))
        updates = [PowerUpdate(reading.power, reading.timestamp, 'reading')]

        cursor = self.db.cursor()
        quarter = round_down_quarter(reading.timestamp)
        cursor.execute('SELECT power_average, num_readings FROM power_quarter_average WHERE timestamp = ?', (quarter,))
        row = cursor.fetchone()
        new_power_average = reading.power
        if row is None:
            self.db.execute('INSERT INTO power_quarter_average VALUES (?, ?, ?)',
                            (quarter, reading.power, 1))
        else:
            power_average, num_readings = row
            new_power_average = (power_average * num_readings + reading.power) / (num_readings + 1)
            self.db.execute('UPDATE power_quarter_average SET power_average = ?, num_readings = ? WHERE timestamp = ?',
                            (new_power_average, num_readings + 1, quarter))

        updates.append(PowerUpdate(new_power_average, quarter, 'average'))

        month, power_max = self.get_power_month_peak(reading.timestamp)
        if new_power_average > power_max:
            self.db.execute('INSERT OR REPLACE INTO power_month_peak VALUES (?, ?)', (month, new_power_average))
            updates.append(PowerUpdate(new_power_average, month, 'peak'))

        self.db.commit()
        return updates

    def get_power_readings(self, start: datetime, end: datetime):
        cursor = self.db.cursor()
        cursor.execute('SELECT power, timestamp FROM power '
                       'WHERE timestamp >= DATETIME(?) AND timestamp <= DATETIME(?) ORDER BY timestamp',
                       (start.isoformat(), end.isoformat()))
        return [PowerReading(*row) for row in cursor.fetchall()]

    # noinspection SqlWithoutWhere
    def delete_data(self):
        self.db.execute('DELETE FROM power')
        self.db.execute('DELETE FROM power_quarter_average')
        self.db.commit()

    def get_power_month_peak(self, timestamp: datetime):
        cursor = self.db.cursor()
        start = beginning_of_month(timestamp)
        cursor.execute('SELECT power_peak FROM power_month_peak '
                       'WHERE timestamp = DATETIME(?)',
                       (start.isoformat(),))
        result = cursor.fetchone()
        if result is None:
            return start, 0
        else:
            return start, result[0]
