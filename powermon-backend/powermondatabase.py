import sqlite3
from datetime import datetime


class PowermonDatabase:
    def __init__(self, database_file):
        self.db = None
        self.db_file = database_file
        self.create_db()

    def create_db(self):
        self.db = sqlite3.connect(self.db_file)
        self.db.execute('CREATE TABLE IF NOT EXISTS power (timestamp DATETIME, power REAL)')
        self.db.commit()

    def insert_power_reading(self, power, timestamp=datetime.now()):
        self.db.execute('INSERT INTO power VALUES (?, ?)', (timestamp, power))
        self.db.commit()
