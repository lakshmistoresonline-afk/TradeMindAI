import datetime
import pytz

class IndianMarketCalendar:
    TZ = pytz.timezone('Asia/Kolkata')

    # NSE Holidays 2026 (Partial List - Primary observed holidays)
    HOLIDAYS_2026 = [
        "2026-01-26", # Republic Day
        "2026-03-06", # Holi
        "2026-03-27", # Good Friday
        "2026-04-14", # Ambedkar Jayanti
        "2026-05-01", # Maharashtra Day
        "2026-08-15", # Independence Day
        "2026-10-02", # Gandhi Jayanti
        "2026-11-08", # Guru Nanak Jayanti
        "2026-12-25"  # Christmas
    ]

    @staticmethod
    def get_current_time_ist():
        return datetime.datetime.now(IndianMarketCalendar.TZ)

    @staticmethod
    def get_current_session(dt=None):
        if dt is None:
            dt = IndianMarketCalendar.get_current_time_ist()
        elif dt.tzinfo is None:
            dt = pytz.utc.localize(dt).astimezone(IndianMarketCalendar.TZ)
        else:
            dt = dt.astimezone(IndianMarketCalendar.TZ)

        date_str = dt.strftime("%Y-%m-%d")

        # 1. Weekend
        if dt.weekday() >= 5:
            return "WEEKEND"

        # 2. Holiday
        if date_str in IndianMarketCalendar.HOLIDAYS_2026:
            return "HOLIDAY"

        # 3. Time-based Sessions
        time_now = dt.time()

        # Pre-market: 09:00 to 09:15
        if datetime.time(9, 0) <= time_now < datetime.time(9, 15):
            return "PRE_MARKET"

        # Normal Open: 09:15 to 15:30
        if datetime.time(9, 15) <= time_now < datetime.time(15, 30):
            return "OPEN"

        # Post-market: 15:30 to 16:00
        if datetime.time(15, 30) <= time_now < datetime.time(16, 0):
            return "POST_MARKET"

        # Closed: All other times
        return "CLOSED"

    @staticmethod
    def is_market_open(dt=None):
        return IndianMarketCalendar.get_current_session(dt) == "OPEN"

    @staticmethod
    def get_data_freshness_status(latest_data_ts: datetime.datetime):
        """
        Determines freshness status based on Indian Market hours.
        """
        now = IndianMarketCalendar.get_current_time_ist()
        session = IndianMarketCalendar.get_current_session(now)

        if latest_data_ts is None:
            return "INVALID_DATA", 0.0

        if latest_data_ts.tzinfo is None:
            latest_data_ts = pytz.utc.localize(latest_data_ts).astimezone(IndianMarketCalendar.TZ)
        else:
            latest_data_ts = latest_data_ts.astimezone(IndianMarketCalendar.TZ)

        age_hours = (now - latest_data_ts).total_seconds() / 3600.0

        if session == "OPEN":
            # During market hours, data should be < 15 mins fresh for signal generation
            if (now - latest_data_ts).total_seconds() > 900:
                return "STALE_MARKET_DATA", age_hours
            return "FRESH", age_hours

        # For non-open sessions, return the session name as status
        return session, age_hours
