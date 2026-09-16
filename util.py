from datetime import timedelta, datetime

def parse_service_time(stop_time: str, today: datetime) -> datetime:
    '''
    Normalize a service time (which can be hours over 24 for times after midnight on each "service day") to be
    a datetime formatted in the UTC format.
    
    :param str stop_time: The time, as a string, to be translated (i.e. 25:01:36 becomes 1:01:36AM the next day)
    :param datetime today: Todays date
    
    :returns datetime: The adjusted time in the datetime UTC format
    '''
    h, m, s = map(int, stop_time.split(":"))
    
    adjusted_date = datetime(
        today.year,
        today.month,
        today.day,
        h % 24,
        m,
        s,
        tzinfo = today.tzinfo
    )
    
    return adjusted_date + timedelta(days = h // 24)