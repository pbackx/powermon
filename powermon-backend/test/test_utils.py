import unittest
from datetime import datetime
from powermon.utils import round_down_quarter


class ToolsTest(unittest.TestCase):
    def test_round_down_quarter(self):
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 0, 1)).second, 0)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 1, 1)).minute, 0)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 1, 1, 1)).hour, 1)

        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 15, 1)).second, 0)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 0, 16, 1)).minute, 15)
        self.assertEqual(round_down_quarter(datetime(2023, 1, 1, 1, 16, 1)).hour, 1)


if __name__ == '__main__':
    unittest.main()
