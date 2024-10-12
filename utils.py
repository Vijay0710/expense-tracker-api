import datetime
from pytz import timezone



def getCurrentTimeStamp():
    return datetime.datetime.now(timezone("Asia/Kolkata"))