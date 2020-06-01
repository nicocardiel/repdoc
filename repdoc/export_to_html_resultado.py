#
# Copyright 2019-2020 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .date_last_update import date_last_update

from .define_gui_layout import COLOR_ASIGNACION_HEAD
from .define_gui_layout import COLOR_ASIGNACION_EVEN
from .define_gui_layout import COLOR_ASIGNACION_ODD

from .definitions import NULL_UUID


def insert_separator(f, height=2):
    cheight = str(height)
    for idum in range(2):
        f.write('\n<tr style="background: ' +
                COLOR_ASIGNACION_HEAD +
                '; height: ' + cheight + 'px; padding-top: 0px; ' +
                'padding-bottom: 0px;">')
        f.write('<td colspan="14" style="height: ' + cheight + 'px; ' +
                'padding-top: 0px; padding-bottom: 0px;">' +
                '</td></tr>\n')


def export_to_html_resultado(
        tabla_profesores,
        bigdict_tablas_asignaturas,
        bitacora, course):
    """Export to html tabla_resultado

    """

    f = open('repdoc_resultado.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>Resultado</title>
  
  <style>
  
  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }
  
  #tabla_resultado {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
    width: 100%;
  }
  
  #tabla_resultado td, #tabla_resultado th {
    border: 1px solid #fff;
    padding: 8px;
  }
  
  #tabla_resultado tr:nth-child(even) {
    background-color: ''' + COLOR_ASIGNACION_EVEN + ''';
  }
  
  #tabla_resultado tr:nth-child(odd) {
    background-color: ''' + COLOR_ASIGNACION_ODD + ''';
  }
  
  #tabla_resultado tr:hover {
    background-color: #ddd;
  }
  
  #tabla_resultado th {
    position: sticky;
    top: 0;
    z-index: 2;
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_ASIGNACION_HEAD + ''';
    color: white;
  }
  
  pre {
    display: inline;
    margin: 0;
  }
  
  @media print  
  {
    div{
        page-break-inside: avoid;
    }
  }
  
  /* Large rounded green border */
  hr.sep {
    border: 3px solid ''' + COLOR_ASIGNACION_HEAD + ''';
  }

  </style>
</head>

<body>

''')

    f.write('''
<h1>Reparto Docente FTA<br><small>Curso {}</small></h1> 
<h2>Resultado final del reparto</h2>
'''.format(course))
    f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')
    f.write('''
<table id="tabla_resultado">

<thead>
<tr style="text-align: left;">
<th>Curso</th>
<th>Semestre</th>
<th>Código</th>
<th>Asignatura</th>
<th>Comentarios</th>
<th>Grupo</th>
<th>Profesor</th>
<th>Categoría</th>
<th>Créditos</th>
</tr>
</thead>

<tbody>

''')


    creditos_totales = 0
    for i, key in enumerate(bigdict_tablas_asignaturas.keys()):
        tabla_asignaturas = bigdict_tablas_asignaturas[key]
        #
        ultima_asignatura = None
        for uuid_asig in tabla_asignaturas.index:
            nueva_asignatura = tabla_asignaturas.loc[uuid_asig]['asignatura']
            if ultima_asignatura is None:
                ultima_asignatura = nueva_asignatura
            else:
                if nueva_asignatura != ultima_asignatura:
                    insert_separator(f)
                    ultima_asignatura = nueva_asignatura

            # subset of bitacora for the selected subject
            seleccion = bitacora.loc[
                (bitacora['uuid_asig'] == uuid_asig) &
                (bitacora['date_removed'] == 'None') &
                (bitacora['uuid_titu'] != NULL_UUID)
            ].copy()
            ntimes = seleccion.shape[0]
            if ntimes == 0:
                f.write('\n<tr>')
                f.write('\n<td>{}</td>\n'.format(
                    tabla_asignaturas.loc[uuid_asig]['curso']
                ))
                f.write('<td style="text-align: center;">{}</td>\n'.format(
                    tabla_asignaturas.loc[uuid_asig]['semestre']
                ))
                f.write('<td style="text-align: center;">{}</td>\n'.format(
                    tabla_asignaturas.loc[uuid_asig]['codigo']

                ))
                f.write('<td>{}</td>\n'.format(
                    tabla_asignaturas.loc[uuid_asig]['asignatura']
                ))
                f.write('<td>{}</td>\n'.format(
                    tabla_asignaturas.loc[uuid_asig]['comentarios']
                ))
                f.write('<td style="text-align: center;">{}</td>\n'.format(
                    tabla_asignaturas.loc[uuid_asig]['grupo']
                ))
                f.write('<td style="text-align: left;"> &mdash; </td>\n')
                f.write('<td style="text-align: center;"> &mdash; </td>\n')
                f.write('<td style="text-align: center;"> &mdash; </td>\n')
            else:
                for i in range(ntimes):
                    f.write('\n<tr>')
                    f.write('\n<td>{}</td>\n'.format(
                        seleccion['curso'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['semestre'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['codigo'].tolist()[i]

                    ))
                    f.write('<td>{}</td>\n'.format(
                        seleccion['asignatura'].tolist()[i]
                    ))
                    comentarios = seleccion['comentarios'].tolist()[i]
                    if len(comentarios) == 0 or comentarios == ' ':
                        comentarios = seleccion['explicacion'].tolist()[i]
                    f.write('<td>{}</td>\n'.format(comentarios))
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['grupo'].tolist()[i]
                    ))
                    categoria = seleccion['categoria'].tolist()[i]
                    if categoria == 'Colaborador':
                        color = '#282'
                    else:
                        color = '#000'
                    f.write('<td style="text-align: left; ' +
                            'color: {};">'.format(color) +
                            '{}</td>\n'.format(
                        seleccion['nombre'].tolist()[i] + ' ' + \
                        seleccion['apellidos'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center; ' +
                            'color: {};">'.format(color) +
                            '{}</td>\n'.format(categoria)
                            )
                    creditos = seleccion['creditos_elegidos'].tolist()[i]
                    f.write('<td style="text-align: center; ' +
                            'color: {};">'.format(color) +
                            '{0:9.4f}</td>\n'.format(creditos)
                            )
                    creditos_totales += creditos

        insert_separator(f, 10)

    f.write('\n</tbody>\n\n')
    #
    f.write('<tfoot>\n\n')
    f.write('<tr>\n')
    f.write('<td colspan="8" style="text-align: right;">SUMA</td>')
    f.write('<td style="text-align: center; font-weight: bold; ' +
            'background-color: ' + COLOR_ASIGNACION_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos_totales) + '</td>\n')
    f.write('</tr>\n')
    #
    f.write('\n</tfoot>\n\n')
    f.write('\n</table>\n\n')
    f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')
    f.write('<hr class="sep"></div>\n\n')

    f.write(date_last_update())
    f.write('</body>\n\n</html>\n')
    f.close()
