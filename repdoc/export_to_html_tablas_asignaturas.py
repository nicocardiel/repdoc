#
# Copyright 2019-2022 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .date_last_update import date_last_update

from .define_gui_layout import COLOR_ASIGNATURAS_HEAD
from .define_gui_layout import COLOR_ASIGNATURAS_EVEN
from .define_gui_layout import COLOR_ASIGNATURAS_ODD
from .define_gui_layout import COLOR_NO_DISPONIBLE


def writeff(f, ff, output):
    f.write(output)
    if ff is not None:
        ff.write(output)


def export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas, course):
    """Export to html bigdict_tablas_asignaturas

    """

    ff = open('repdoc_disponibles.html', 'wt')

    for i, key in enumerate(bigdict_tablas_asignaturas.keys()):
        tabla_asignaturas = bigdict_tablas_asignaturas[key]
        #
        f = open('repdoc_titulacion_{:02d}.html'.format(i + 1), 'wt')
        if i == 0:
            fff = ff
        else:
            fff = None
        writeff(f, fff, '''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>''' + key + '''</title>

  <style>

  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }
  
  #tabla_asignaturas {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
  }

  #tabla_asignaturas td, #tabla_asignaturas th {
    border: 1px solid #fff;
    padding: 8px;
  }

  #tabla_asignaturas tr:nth-child(even) {
    background-color: ''' + COLOR_ASIGNATURAS_EVEN + ''';
  }

  #tabla_asignaturas tr:nth-child(odd) {
    background-color: ''' + COLOR_ASIGNATURAS_ODD + ''';
  }

  #tabla_asignaturas tr:hover {
    background-color: #ddd;
  }

  #tabla_asignaturas th {
    position: sticky;
    top: 0;
    z-index: 2;
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_ASIGNATURAS_HEAD + ''';
    color: white;
  }

  </style>
</head>

<body>

''')

        writeff(
            f, fff,
            '<h1>Reparto Docente FTA<br><small>Curso {}</small></h1>\n'.format(course)
        )
        f.write('<h2>Listado de asignaturas: {}</h2>\n'.format(key))
        ff.write('<h2>Listado de asignaturas disponibles: {}</h2>\n'.format(
            key))

        writeff(f, ff, '<p><a href="index.html">Volver a la página principal'
                '</a></p>\n')

        writeff(f, ff, '''
<table id="tabla_asignaturas">

<thead>
<tr style="text-align: left;">
<td style="background: #fff;"></td>
<th>Curso</th>
<th>Semestre</th>
<th>Código</th>
<th>Asignatura</th>
<th>Área</th>
<th>Créditos iniciales</th>
<th>Comentarios</th>
<th>Grupo</th>
<th>Bec./Col.</th>
<th>Profesor curso anterior</th>
<th>Antigüedad curso anterior</th>
<th>Profesor próximo curso</th>
<th>Créditos disponibles</th>
</tr>
</thead>

<tbody>

''')

        def insert_separator():
            for idum in range(2):
                if not separator_ff:
                    fff = ff
                else:
                    fff = None
                writeff(f, fff, '\n<tr style="background: ' +
                        COLOR_ASIGNATURAS_HEAD +
                        '; height: 2px; padding-top: 0px; ' +
                        'padding-bottom: 0px;">')
                writeff(f, fff, '<td colspan="14" style="height: 2px; ' +
                        'padding-top: 0px; padding-bottom: 0px;">' +
                        '</td></tr>\n')

        ultima_asignatura = None
        separator_ff = False
        for uuid_asig in tabla_asignaturas.index:
            irow = tabla_asignaturas.loc[uuid_asig]['num']
            nueva_asignatura = tabla_asignaturas.loc[uuid_asig]['asignatura']
            if ultima_asignatura is None:
                ultima_asignatura = nueva_asignatura
            else:
                if nueva_asignatura != ultima_asignatura:
                    insert_separator()
                    ultima_asignatura = nueva_asignatura
                    separator_ff = True
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_disponibles']
            if creditos > 0:
                writeff(f, ff, '\n<tr>\n')
                fff = ff
                separator_ff = False
            else:
                f.write(
                    '\n<tr style="background: ' + COLOR_NO_DISPONIBLE + ';">\n'
                )
                fff = None
            writeff(f, fff,
                    '<td style="color: #888; background: #fff; text-align: '
                    'right;">')
            writeff(f, fff, '{:d}</td>\n'.format(irow))
            writeff(f, fff, '<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['curso']
            ))
            writeff(f, fff, '<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['semestre']
            ))
            writeff(f, fff, '<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['codigo']
            ))
            writeff(f, fff, '<td>{}</td>\n'.format(nueva_asignatura))
            writeff(f, fff, '<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['area']
            ))
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_iniciales']
            writeff(f, fff, '<td style="text-align: right;">' +
                    '{0:9.4f}'.format(creditos) + '</td>\n')
            writeff(f, fff, '<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['comentarios']
            ))
            writeff(f, fff, '<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['grupo']
            ))
            writeff(f, fff, '<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['bec_col']
            ))
            writeff(f, fff, '<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['profesor_anterior']
            ))
            writeff(f, fff, '<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['antiguedad']
            ))
            writeff(f, fff, '<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['nuevo_profesor']
            ))
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_disponibles']
            writeff(f, fff, '<td style="text-align: right;">' +
                    '{0:9.4f}'.format(creditos) + '</td>\n'
                    )
            writeff(f, fff, '</tr>\n')

        insert_separator()
        writeff(f, ff, '\n</tbody>\n\n')
        #
        writeff(f, ff, '<tfoot>\n\n')
        writeff(f, ff, '<tr>\n')
        f.write('<td colspan="6" style="text-align: right;">SUMA</td>\n')
        creditos = tabla_asignaturas['creditos_iniciales'].sum()
        f.write('<td style="text-align: right; font-weight: bold; ' +
                'background-color: ' + COLOR_ASIGNATURAS_HEAD +
                '; color: white;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        ff.write('<td colspan="7" style="text-align: right;"> </td>\n')
        writeff(f, ff,
                '<td colspan="6" style="text-align: right;">SUMA</td>\n')
        creditos = tabla_asignaturas['creditos_disponibles'].sum()
        writeff(f, ff, '<td style="text-align: right; font-weight: bold; ' +
                'background-color: ' + COLOR_ASIGNATURAS_HEAD +
                '; color: white;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        writeff(f, ff, '\n</tfoot>\n\n')
        #
        writeff(f, ff, '\n</table>\n\n')
        writeff(f, ff, '<p><a href="index.html">Volver a la página principal'
                '</a></p>\n')
        f.write(date_last_update())
        writeff(f, ff, '</body>\n\n</html>\n')
        f.close()

    ff.write(date_last_update())
    ff.close()
