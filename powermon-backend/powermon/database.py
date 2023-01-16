import sqlite3
from .model import PowerReading
from .utils import round_down_quarter


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
        self.db.commit()

    def insert_power_reading(self, reading: PowerReading):
        self.db.execute('INSERT INTO power VALUES (?, ?)', (reading.timestamp, reading.power))

        cursor = self.db.cursor()
        quarter = round_down_quarter(reading.timestamp)
        cursor.execute('SELECT power_average, num_readings FROM power_quarter_average WHERE timestamp = ?', (quarter,))
        row = cursor.fetchone()
        if row is None:
            self.db.execute('INSERT INTO power_quarter_average VALUES (?, ?, ?)',
                            (quarter, reading.power, 1))
        else:
            power_average, num_readings = row
            new_power_average = (power_average * num_readings + reading.power) / (num_readings + 1)
            self.db.execute('UPDATE power_quarter_average SET power_average = ?, num_readings = ? WHERE timestamp = ?',
                            (new_power_average, num_readings + 1, quarter))

        self.db.commit()

    def get_power_readings(self, start, end):
        cursor = self.db.cursor()
        cursor.execute('SELECT power, timestamp FROM power '
                       'WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp',
                       (start, end))
        return [PowerReading(*row) for row in cursor.fetchall()]

    # noinspection SqlWithoutWhere
    def delete_data(self):
        self.db.execute('DELETE FROM power')
        self.db.execute('DELETE FROM power_quarter_average')
        self.db.commit()