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


def export_to_html_bitacora(bitacora, filename, course):
    """Export bitacora to html and xlsx files

    """

    if filename is None:
        fname = DEFAULT_BITACORA_XLSX_FILENAME
    else:
        fname = filename.name
    bitacora.to_excel(fname, header=True)

    f = open('repdoc_bitacora.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>Bitácora</title>

  <style>

  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }

  #tabla_bitacora {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
  }

  #tabla_bitacora td, #tabla_bitacora th {
    border: 1px solid #fff;
    padding: 8px;
  }

  #tabla_bitacora tr:nth-child(even) {
    background-color: ''' + COLOR_BITACORA_EVEN + ''';
  }

  #tabla_bitacora tr:nth-child(odd) {
    background-color: ''' + COLOR_BITACORA_ODD + ''';
  }

  #tabla_bitacora tr:hover {
    background-color: #ddd;
  }

  #tabla_bitacora th {
    position: sticky;
    top: 0;
    z-index: 2;
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_BITACORA_HEAD + ''';
    color: white;
  }

  </style>
</head>

<body>

''')

    f.write('''
<h1>Reparto Docente FTA<br><small>Curso {}</small></h1> 
<h2>Cuaderno de bitácora</h2>
'''.format(course))
    f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')

    f.write('''
<table id="tabla_bitacora">

<thead>
<tr style="text-align: left;">
''')

    f.write('<td style="background: #fff;"></td>')
    f.write('<th style="text-align: center;">(1)<br>uuid bita</th>\n')
    icol = 1
    for colname in bitacora.columns.tolist():
        icol += 1
        f.write('<th style="text-align: center;">' +
                '({:d})<br>'.format(icol) +
                re.sub('_', ' ', colname) + '</th>\n')

    f.write('''
</tr>
</thead>

<tbody>

''')

    irow = len(bitacora.index) + 1
    for uuid_bita in reversed(bitacora.index):
        irow -= 1
        status = str(bitacora.loc[uuid_bita]['date_removed']) == 'None'
        if status:
            f.write('\n<tr>\n')
        else:
            f.write(
                '\n<tr style="background: ' + COLOR_NO_DISPONIBLE + ';">\n'
            )
        f.write('<td style="color: #888; background: #fff; text-align: '
                'right;">')
        f.write('{:d}</td>\n'.format(irow))
        f.write('<td>{}</td>\n'.format(uuid_bita))
        for colname in bitacora.columns.tolist():
            typecol = type(bitacora.loc[uuid_bita][colname])
            if typecol == np.dtype(np.int):
                f.write('<td style="text-align: center;">{}</td>\n'.format(
                    bitacora.loc[uuid_bita][colname]
                ))
            elif typecol == np.dtype(np.float):
                f.write('<td style="text-align: center;">{}</td>\n'.format(
                    round(bitacora.loc[uuid_bita][colname], 4)
                ))
            else:
                f.write('<td>{}</td>\n'.format(
                    bitacora.loc[uuid_bita][colname]
                ))
        f.write('</tr>\n')

    f.write('\n</tbody>\n\n')
    f.write('\n</table>\n\n')
    f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')

    f.write(date_last_update())
    f.write('</body>\n\n</html>\n')
    f.close()
