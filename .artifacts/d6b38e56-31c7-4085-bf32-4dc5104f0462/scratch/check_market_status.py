import sys
import os
import pytz
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from backend.services.market_calendar import IndianMarketCalendar

now = IndianMarketCalendar.get_current_time_ist()
session = IndianMarketCalendar.get_current_session(now)

print(f"IST Time: {now}")
print(f"Market Status: {session}")
print(f"Is Market Open: {IndianMarketCalendar.is_market_open(now)}")
