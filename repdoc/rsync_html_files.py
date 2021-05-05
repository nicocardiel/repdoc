#
# Copyright 2019-2021 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import subprocess
import yaml


def rsync_html_files(course=None, xlsxfile=None, bitacora=None):
    """Execute rsync of HTML files to server

    """

    if course is None:
        raise ValueError('Unexpected course=None value')

    conf = yaml.load(open('configuration.yaml'), Loader=yaml.FullLoader)
    username = conf['user']['username']
    machine = conf['user']['machine']
    directory = conf['user']['directory']
    address = username + '@' + machine + ':' + directory

    command = 'rsync -arv --delete *html '
    command += 'last_execution_command.txt '
    if xlsxfile is not None:
        command += xlsxfile.name + ' '
    if bitacora is not None:
        command += bitacora.name + ' '
    command += address
    command += course
    command += '/'

    print('--> Executing rsync:\n' + command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print(p.stdout.read().decode('utf-8'))
    p.stdout.close()
    p.wait()
