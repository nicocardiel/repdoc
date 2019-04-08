from datetime import datetime


def date_last_update():
    """Return current date

    """

    now = datetime.now()
    return '\n\n<br><br>Last update: ' + \
           '{:4d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
               now.year, now.month, now.day, now.hour, now.minute, now.second
           ) + '\n\n'
