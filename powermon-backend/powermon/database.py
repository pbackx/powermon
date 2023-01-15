import sqlite3
from model import PowerReading


class PowermonDatabase:
    def __init__(self, database_file):
        self.db = None
        self.db_file = database_file
        self.create_db()

    def create_db(self):
        self.db = sqlite3.connect(self.db_file)
        self.db.execute('CREATE TABLE IF NOT EXISTS power (timestamp DATETIME, power REAL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS power_quarter_average '
                        '(timestamp DATETIME, power_quarter_average REAL, num_readings INTEGER)')
        self.db.commit()

    def insert_power_reading(self, reading: PowerReading):
        self.db.execute('INSERT INTO power VALUES (?, ?)', (reading.timestamp, reading.power))
        self.db.commit()

    def get_power_readings_from_quarter(self, reading: PowerReading):
        """
        Get all power readings from the quarter of the hour that the given reading is in.
        """
        pass