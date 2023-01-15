from datetime import datetime


def round_down_quarter(dt: datetime) -> datetime:
    return dt.replace(minute=15 * (dt.minute // 15), second=0, microsecond=0)
