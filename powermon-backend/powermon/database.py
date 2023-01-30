import functools
import sqlite3
from datetime import datetime, timedelta

from .model import PowerReading, PowerUpdate, PowerUpdateType
from .utils import round_down_quarter, beginning_of_month


class PowermonDatabase:
    def __init__(self, database_file, local_timezone):
        self.db = None
        self.db_file = database_file
        self.create_db()
        self.local_timezone = local_timezone

    def create_db(self):
        self.db = sqlite3.connect(self.db_file)
        self.db.execute('CREATE TABLE IF NOT EXISTS power (timestamp DATETIME, power REAL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS power_quarter_average '
                        '(timestamp DATETIME, power_average REAL, num_readings INTEGER)')
        self.db.execute('CREATE TABLE IF NOT EXISTS power_month_peak'
                        '(timestamp DATETIME PRIMARY KEY, power_peak REAL)')
        self.db.commit()

    def insert_power_reading(self, reading: PowerReading) -> list[PowerUpdate]:
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
        updates.append(self.update_month_peak())

        self.db.commit()
        return updates

    def get_power_readings(self, start: datetime, end: datetime):
        cursor = self.db.cursor()
        cursor.execute('SELECT power, timestamp FROM power '
                       'WHERE timestamp >= DATETIME(?) AND timestamp <= DATETIME(?) ORDER BY timestamp',
                       (start.isoformat(), end.isoformat()))
        return [PowerUpdate(*row, 'reading') for row in cursor.fetchall()]

    def get_power_averages(self, start: datetime, end: datetime) -> list[PowerUpdate]:
        cursor = self.db.cursor()
        cursor.execute('SELECT power_average, timestamp FROM power_quarter_average '
                       'WHERE timestamp >= DATETIME(?) AND timestamp <= DATETIME(?) ORDER BY timestamp',
                       (start.isoformat(), end.isoformat()))
        return [PowerUpdate(*row, 'average') for row in cursor.fetchall()]

    def get_month_peaks(self, start: datetime, end: datetime) -> list[PowerUpdate]:
        cursor = self.db.cursor()
        cursor.execute('SELECT power_peak, timestamp FROM power_month_peak '
                       'WHERE timestamp >= DATETIME(?) AND timestamp <= DATETIME(?) ORDER BY timestamp',
                       (start.isoformat(), end.isoformat()))
        return [PowerUpdate(*row, PowerUpdateType.PEAK) for row in cursor.fetchall()]

    def get_yearly_average(self, month_peaks: list[PowerUpdate] = None):
        if month_peaks is None:
            start = datetime.now(self.local_timezone) - timedelta(days=365)
            end = datetime.now(self.local_timezone)
            month_peaks = self.get_month_peaks(start, end)
        average = sum([peak.power for peak in month_peaks]) / len(month_peaks)
        return PowerUpdate(average, datetime.now(self.local_timezone), PowerUpdateType.YEAR_AVERAGE)

    # noinspection SqlWithoutWhere

    def delete_data(self):
        self.db.execute('DELETE FROM power')
        self.db.execute('DELETE FROM power_quarter_average')
        self.db.execute('DELETE FROM power_month_peak')
        self.db.commit()

    def update_month_peak(self) -> PowerUpdate:
        now = datetime.now(self.local_timezone)
        month = beginning_of_month(now)
        averages = self.get_power_averages(month, now)
        peak = functools.reduce(lambda q1, q2: q1 if q1.power > q2.power else q2, averages)
        self.db.execute('INSERT OR REPLACE INTO power_month_peak VALUES (?, ?)', (month, peak.power))

        return PowerUpdate(peak.power, month, 'peak')
