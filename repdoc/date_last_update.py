#
# Copyright 2019 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

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
<br>
<p style="color: #000; width: 100%; background-color: #ddd; 
text-align: center;">
Last update: ''' + datetime_short() + '''\n
&nbsp; &mdash; &nbsp; Created with 
<a href="https://github.com/nicocardiel/repdoc">RepDoc</a>
version ''' + version + '''
\n&nbsp; &mdash; &nbsp; 
Copyright &copy; 2019 Universidad Complutense de Madrid</p>\n\n'''
