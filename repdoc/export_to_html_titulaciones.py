#
# Copyright 2019-2022 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .date_last_update import date_last_update

from .define_gui_layout import COLOR_NO_DISPONIBLE
from .define_gui_layout import COLOR_TITULACIONES_HEAD
from .define_gui_layout import COLOR_TITULACIONES_EVEN
from .define_gui_layout import COLOR_TITULACIONES_ODD


def export_to_html_titulaciones(tabla_titulaciones, course):
    """Export to html tabla_titulaciones

    """

    f = open('repdoc_titulaciones.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>FTA, {}</title>\n\n'''.format(course))

    f.write('''
  <style>

  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }
  
  #tabla_titulaciones {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
  }

  #tabla_titulaciones td, #tabla_titulaciones th {
    border: 1px solid #fff;
    padding: 8px;
  }

  #tabla_titulaciones tr:nth-child(even) {
    background-color: ''' + COLOR_TITULACIONES_EVEN + ''';
  }
  #tabla_titulaciones tr:nth-child(odd) {
    background-color: ''' + COLOR_TITULACIONES_ODD + ''';
  }

  #tabla_titulaciones tr:hover {
    background-color: #ddd;
  }

  #tabla_titulaciones th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_TITULACIONES_HEAD + ''';
    color: white;
  }

  </style>
</head>

<body>

''')

    f.write('''
<h1>Reparto Docente FTA<br><small>Curso {}</small></h1> 
<h2>Tablas relevantes durante el reparto docente</h2>
<p></p>
<p>Enlace a tabla resumen de 
<a href="repdoc_profesores.html">Profesores/as</a></p>
<p></p>
<p>Enlace a tabla de 
<a href="repdoc_asignacion.html">asignación de asignaturas</a> por profesor/a</p>
<p></p>
<p>Enlace a tabla con
<a href="repdoc_disponibles.html">solo asignaturas disponibles 
</a> (todas las titulaciones) durante el reparto</p>
<p></p>
<p>Enlace al
<a href="repdoc_bitacora.html">cuaderno de bitácora</a>
del reparto docente</p>
<p></p>
'''.format(course))

    f.write('''
<table id="tabla_titulaciones">

<thead>
<tr><td colspan="5" style="text-align: center; font-size: 20px; 
color: ''' + COLOR_TITULACIONES_HEAD + ";" + '''
font-weight: bold;">Tabla resumen de titulaciones</td></tr>
<tr style="text-align: left;">
<th>Titulación</th>
<th style="text-align: center;">Créditos iniciales</th>
<th style="text-align: center;">Créditos elegidos</th>
<th style="text-align: center;">Créditos disponibles</th>
<th style="text-align: center;">Créditos para Bec./Col.</th>
</tr>
</thead>

<tbody>

''')

    for i, uuid_titu in enumerate(tabla_titulaciones.index):
        creditos = tabla_titulaciones.loc[uuid_titu]['creditos_disponibles']
        if creditos > 0:
            f.write('\n<tr>\n')
        else:
            f.write(
                '\n<tr style="background: ' + COLOR_NO_DISPONIBLE + ';">\n'
            )
        f.write('<td><a href="repdoc_titulacion_{0:02d}.html">'.format(i + 1))
        f.write('{}</a></td>\n'.format(
            tabla_titulaciones.loc[uuid_titu]['titulacion']
        ))
        creditos = tabla_titulaciones.loc[uuid_titu]['creditos_iniciales']
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        creditos = tabla_titulaciones.loc[uuid_titu]['creditos_elegidos']
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        creditos = tabla_titulaciones.loc[uuid_titu]['creditos_disponibles']
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        creditos = tabla_titulaciones.loc[uuid_titu]['creditos_beccol']
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        f.write('</tr>\n')

    f.write('\n</tbody>\n\n')
    #
    f.write('<tfoot>\n\n')
    f.write('<tr>\n')
    f.write('<td colspan="1" style="text-align: right;">TOTAL</td>\n')
    creditos = tabla_titulaciones['creditos_iniciales'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_titulaciones['creditos_elegidos'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_titulaciones['creditos_disponibles'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_titulaciones['creditos_beccol'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')

    f.write('\n</tfoot>\n\n')
    #
    f.write('\n</table><br>\n\n')

    f.write('''
    <p></p>
    <h2>Resultado del reparto docente</h2>
    <p></p>
    <p>Enlace a
    <a href="repdoc_resultado.html">tabla final</a></p>
    ''')

    f.write(date_last_update())
    f.write('</body>\n\n</html>\n')
    f.close()
