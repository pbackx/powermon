from datetime import datetime


def round_down_quarter(dt: datetime) -> datetime:
    return dt.replace(minute=15 * (dt.minute // 15), second=0, microsecond=0)


def beginning_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
