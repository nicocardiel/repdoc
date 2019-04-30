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

    return '''\n\n
<br><br>
<p style="color: #999; width: 100%; background-color: #ddd; 
text-align: center;">
Last update: ''' + datetime_short() + '''\n
&nbsp; &mdash; &nbsp; Created with RepDoc version ''' + version + '''
\n&nbsp; &mdash; &nbsp; 
Copyright &copy; 2019 Universidad Complutense de Madrid</p>\n\n'''
