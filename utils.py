import datetime

def schedule_reminder(task: str, time_str: str, date_str: str):
    """
    Given a task, a time string (e.g., '3pm'), and a date string (YYYY-MM-DD),
    convert these into a datetime object representing when the reminder is set.
    """
    try:
        # Parse the time string (expects format like "3pm" or "11am")
        time_obj = datetime.datetime.strptime(time_str.lower(), "%I%p").time()
    except ValueError:
        raise ValueError("Time format error: please use a format like '3pm' or '11am'.")
    
    try:
        # Parse the date string (expects format YYYY-MM-DD)
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date format error: please use YYYY-MM-DD format.")
    
    return datetime.datetime.combine(date_obj, time_obj)