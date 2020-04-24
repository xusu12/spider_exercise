import time
from datetime import datetime

import pytz


def return_PST():
    # 设置为洛杉矶时区
    time_zone = pytz.timezone('America/Los_Angeles')
    dateNow = datetime.now(time_zone)
    return dateNow


data = datetime.date(return_PST())
tt = str(data)+" "+"15:00:00"
timeArray = time.strptime(tt, "%Y-%m-%d %H:%M:%S")
tm = int(round(time.mktime(timeArray)*1000))
print(tm)