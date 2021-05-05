#
# Copyright 2019-2021 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import numpy as np
import re

from .date_last_update import date_last_update

from .define_gui_layout import COLOR_BITACORA_HEAD
from .define_gui_layout import COLOR_BITACORA_EVEN
from .define_gui_layout import COLOR_BITACORA_ODD
from .define_gui_layout import COLOR_NO_DISPONIBLE
from .definitions import DEFAULT_BITACORA_XLSX_FILENAME


def export_to_html_index(course):
    """Generate index.htmlfile

    """

    f = open('index.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <meta HTTP-EQUIV="Refresh" CONTENT="0; URL=repdoc_titulaciones.html">
  <title>Reparto Docente FTA, curso {}</title>
</head>

<body>

Please wait...

</body>

</html>
'''.format(course))
    f.close()
