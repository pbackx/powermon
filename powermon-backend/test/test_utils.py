import unittest
from datetime import datetime
from powermon.utils import round_down_quarter, beginning_of_month


class ToolsTest(unittest.TestCase):
    def test_round_down_quarter(self):
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 0, 1)).second, 0)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 15, 0)).minute, 15)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 15, 1)).minute, 15)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 1, 1)).minute, 0)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 1, 1, 1)).hour, 1)

        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 15, 1)).second, 0)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 16, 1)).minute, 15)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 1, 16, 1)).hour, 1)

        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 59, 0)).minute, 45)

    def test_beginning_of_month(self):
        self.assertEqual(beginning_of_month(datetime(2023, 10, 1, 0, 0, 0)).day, 1)
        self.assertEqual(beginning_of_month(datetime(2023, 10, 1, 0, 0, 0)).month, 10)
        self.assertEqual(beginning_of_month(datetime(2023, 10, 1, 0, 0, 0)).year, 2023)


if __name__ == '__main__':
    unittest.main()
