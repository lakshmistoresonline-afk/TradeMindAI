import datetime
import pytz

class MarketCalendar:
    """
    NSE Market Hours & Holiday Calendar.
    """

    NSE_TZ = pytz.timezone('Asia/Kolkata')

    @staticmethod
    def is_market_open() -> bool:
        now = datetime.datetime.now(MarketCalendar.NSE_TZ)

        # 1. Weekends
        if now.weekday() >= 5:
            return False

        # 2. Market Hours (09:15 - 15:30)
        start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        end = now.replace(hour=15, minute=30, second=0, microsecond=0)

        if now < start or now > end:
            return False

        # 3. Static Holiday Check (Placeholder for institutional list)
        holidays = [
            datetime.date(2026, 1, 26), # Republic Day
            datetime.date(2026, 8, 15), # Independence Day
            datetime.date(2026, 10, 2), # Gandhi Jayanti
        ]
        if now.date() in holidays:
            return False

        return True

    @staticmethod
    def get_next_market_open() -> datetime.datetime:
        # Simplified: Return 9:15 AM IST next business day
        now = datetime.datetime.now(MarketCalendar.NSE_TZ)
        next_day = now + datetime.timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += datetime.timedelta(days=1)
        return next_day.replace(hour=9, minute=15, second=0)
