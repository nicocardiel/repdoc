from datetime import datetime

from .version import version


def datetime_short():
    """Return current datetime, rounded to seconds"""
    now = datetime.now()
    return '{:4d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
               now.year, now.month, now.day, now.hour, now.minute, now.second
           )



def date_last_update():
    """Return current date

    """

    return '\n\n<br><br>Last update: ' + datetime_short() + \
           '\n<br>Created with repdoc v. ' + version + \
           ', (c) N. Cardiel\n\n'
