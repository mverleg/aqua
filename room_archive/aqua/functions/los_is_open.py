
from datetime import time


def los_is_open(day):
    now = time(day.hour, day.minute)
    if day.weekday() <= 4:
        if now >= time(8, 30) and now <= time(22, 00):
            return True
    if day.weekday() == 5:
        if now >= time(8, 30) and now <= time(17, 30):
            return True
    if day.weekday() == 6:
        if now >= time(9, 30) and now <= time(16, 00):
            return True
    return False

