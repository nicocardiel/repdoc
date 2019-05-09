#
# Copyright 2019 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import subprocess


def rsync_html_files(course=None, xlsxfile=None, bitacora=None):
    """Execute rsync of HTML files to server

    """

    if course is None:
        raise ValueError('Unexpected course=None value')

    command = 'rsync -arv --delete *html '
    command += 'last_execution_command.txt z_leeme.txt '
    if xlsxfile is not None:
        command += xlsxfile.name + ' '
    if bitacora is not None:
        command += bitacora.name + ' '
    command += 'ncl@nartex.fis.ucm.es:public_html/repdoc/'
    command += course
    command += '/'

    print('--> Executing rsync:\n' + command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print(p.stdout.read().decode('utf-8'))
    p.stdout.close()
    p.wait()
