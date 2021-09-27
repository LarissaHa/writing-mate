from datetime import datetime, timedelta, date
from dateutil import rrule


def time_between(start_date, end_date, mode):
    if start_date > end_date:
        raise ValueError(f"Start date {start_date} is not before end date {end_date}")
    mode_transfer = {"daily": rrule.DAILY, "weekly": rrule.WEEKLY, "monthly": rrule.MONTHLY, "yearly": rrule.YEARLY}
    for dt in rrule.rrule(mode_transfer[mode], dtstart=start_date, until=end_date):
        yield(dt)