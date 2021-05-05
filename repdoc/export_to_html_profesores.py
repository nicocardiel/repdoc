#
# Copyright 2019-2021 Universidad Complutense de Madrid
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
from .define_gui_layout import COLOR_NO_DISPONIBLE
from .define_gui_layout import COLOR_PROFESORES_HEAD
from .define_gui_layout import COLOR_PROFESORES_EVEN
from .define_gui_layout import COLOR_PROFESORES_ODD

from .definitions import FLAG_RONDA_NO_ELIGE
from .definitions import NULL_UUID


def export_to_html_profesores(tabla_profesores, bitacora, ronda_actual, course):
    """Export to html tabla_profesores

    """

    # tabla de profesores

    # tabla_profesores.to_html('repdoc_profesores.html')
    f = open('repdoc_profesores.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>Profesores</title>
  
  <style>
  
  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }
  
  #tabla_profesores {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
  }
  
  #tabla_profesores td, #tabla_profesores th {
    border: 1px solid #fff;
    padding: 8px;
  }
  
  #tabla_profesores tr:nth-child(even) {
    background-color: ''' + COLOR_PROFESORES_EVEN + ''';
  }
  
  #tabla_profesores tr:nth-child(odd) {
    background-color: ''' + COLOR_PROFESORES_ODD + ''';
  }
  
  #tabla_profesores tr:hover {
    background-color: #ddd;
  }
  
  #tabla_profesores th {
    position: sticky;
    top: 0;
    z-index: 2;
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_PROFESORES_HEAD + ''';
    color: white;
  }
  
  </style>
</head>

<body>

''')

    f.write('''
<h1>Reparto Docente FTA<br><small>Curso {}</small></h1> 
<h2>Listado de profesores</h2>
'''.format(course))
    f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')

    f.write('<p>Ronda actual: {0:d}</p>\n'.format(ronda_actual))

    f.write('''
<table id="tabla_profesores">

<thead>
<tr style="text-align: left;">
<td style="background: #fff;"></td>
<th>Apellidos</th>
<th>Nombre</th>
<th>Categoría</th>
<th style="text-align: center;">Encargo<br>docente</th>
<th style="text-align: center;">Créditos<br>asignados</th>
<th>Diferencia</th>
<th>Porcentange<br>asignado (%)</th>
<th style="text-align: center;">Siguiente<br>ronda</th>
<th style="text-align: center;">Fin de<br>elección</th>
</tr>
</thead>

<tbody>

''')

    def insert_separator():
        for idum in range(2):
            f.write('\n<tr style="background: ' +
                    COLOR_PROFESORES_HEAD +
                    '; height: 2px; padding-top: 0px; ' +
                    'padding-bottom: 0px;">')
            f.write('<td colspan="10" style="height: 2px; ' +
                    'padding-top: 0px; padding-bottom: 0px;">' +
                    '</td></tr>\n')

    ultima_categoria = None
    for uuid_prof in tabla_profesores.index:
        iprof = tabla_profesores.loc[uuid_prof]['num']
        categoria = tabla_profesores.loc[uuid_prof]['categoria']
        if ultima_categoria is None:
            ultima_categoria = categoria
        else:
            if categoria != ultima_categoria:
                if 'RyC' in categoria and 'RyC' in ultima_categoria:
                    pass
                else:
                    insert_separator()
                ultima_categoria = categoria
        creditos_encargo = tabla_profesores.loc[uuid_prof]['encargo']
        creditos_asignados = tabla_profesores.loc[uuid_prof]['asignados']
        creditos_diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
        if creditos_encargo <= 0:
            porcentage_asignado = 0
        else:
            porcentage_asignado = 100 * creditos_asignados / creditos_encargo
        ronda = tabla_profesores.loc[uuid_prof]['ronda']
        finalizado = tabla_profesores.loc[uuid_prof]['finalizado']
        #
        if (ronda == 99) or (finalizado and ronda_actual != 0):
            f.write('\n<tr style="background: ' + COLOR_NO_DISPONIBLE +
                    ';">\n')
        else:
            if ronda_actual == 0:
                f.write('\n<tr>\n')
            else:
                if (categoria == 'Colaborador') or (ronda > ronda_actual):
                    f.write('\n<tr style="background: ' + COLOR_NO_DISPONIBLE +
                            ';">\n')
                else:
                    f.write('\n<tr>\n')
        #
        f.write('<td style="color: #888; background: #fff; text-align: '
                'right;">')
        f.write('{:d}</td>\n'.format(iprof))
        #
        f.write('<td><a href="repdoc_asignacion.html#')
        f.write(uuid_prof)
        f.write('">')
        f.write(tabla_profesores.loc[uuid_prof]['apellidos'])
        f.write('</a></td>\n')
        f.write('<td><a href="repdoc_asignacion.html#')
        f.write(uuid_prof)
        f.write('">')
        f.write(tabla_profesores.loc[uuid_prof]['nombre'])
        f.write('</a></td>\n')
        f.write('<td>' + categoria + '</td>\n')
        #
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos_encargo) + '</td>\n')
        #
        if creditos_asignados == 0:
            f.write('<td style="text-align: right;">' +
                    '{0:9.4f}'.format(creditos_asignados) + '</td>\n')
        else:
            f.write('<td style="text-align: right;">' +
                    '<a href="repdoc_asignacion.html#' +
                    uuid_prof + '">' +
                    '{0:9.4f}'.format(creditos_asignados) + '</a></td>\n')
        #
        if abs(creditos_diferencia) <= 1e-5:
            color = '#000'
        elif creditos_diferencia < 0:
            color = '#a00'
        else:
            color = '#0a0'
        f.write('<td style="text-align: right; color: ' + color + ';">' +
                '{0:9.4f}'.format(creditos_diferencia) + '</td>\n')
        #
        if creditos_encargo <= 0:
            f.write('<td style="text-align: center;"> &mdash; </td>\n')
        else:
            f.write('<td style="text-align: center; color: ' + color + ';">' +
                    '{0:9.1f}'.format(porcentage_asignado) + '</td>\n')
        #
        if ronda == FLAG_RONDA_NO_ELIGE:
            f.write('<td style="text-align: center;"> &mdash; </td>\n')
        else:
            if finalizado:
                f.write('<td style="text-align: center;">' +
                        '({:d})'.format(ronda) + '</td>\n')
            else:
                f.write('<td style="text-align: center;">' +
                        '{:d}'.format(ronda) + '</td>\n')
        #
        if finalizado:
            f.write('<td style="text-align: center;"> Sí </td>\n')
        else:
            f.write('<td style="text-align: center;"> No </td>\n')
        f.write('</tr>\n')
    f.write('\n</tbody>\n\n')
    #
    f.write('<tfoot>\n\n')
    f.write('<tr>\n')
    f.write('<td colspan="4" style="text-align: right;">SUMA</td>')
    creditos_encargo = tabla_profesores['encargo'].sum()
    creditos_asignados = tabla_profesores['asignados'].sum()
    creditos_diferencia = tabla_profesores['diferencia'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_PROFESORES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos_encargo) + '</td>\n')
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_PROFESORES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos_asignados) + '</td>\n')
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_PROFESORES_HEAD +
            '; color: white;">' +
            '{0:9.4f}'.format(creditos_diferencia) + '</td>\n')
    f.write('</tr>\n')
    #
    f.write('\n</tfoot>\n\n</table>\n\n')
    f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')
    f.write(date_last_update())
    f.write('</body>\n\n</html>\n')
    f.close()

    # tabla de asignación por profesor

    if bitacora is not None:
        f = open('repdoc_asignacion.html', 'wt')
        f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>Asignación</title>
  
  <style>
  
  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }
  
  #tabla_asignacion {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
    width: 100%;
  }
  
  #tabla_asignacion td, #tabla_asignacion th {
    border: 1px solid #fff;
    padding: 8px;
  }
  
  #tabla_asignacion tr:nth-child(even) {
    background-color: ''' + COLOR_ASIGNACION_EVEN + ''';
  }
  
  #tabla_asignacion tr:nth-child(odd) {
    background-color: ''' + COLOR_ASIGNACION_ODD + ''';
  }
  
  #tabla_asignacion tr:hover {
    background-color: #ddd;
  }
  
  #tabla_asignacion th {
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
<h2>Asignación de asignaturas por profesor</h2>
'''.format(course))

        for uuid_prof in tabla_profesores.index:
            iprof = tabla_profesores.loc[uuid_prof]['num']
            creditos_encargo = tabla_profesores.loc[uuid_prof]['encargo']
            creditos_asignados = tabla_profesores.loc[uuid_prof]['asignados']
            creditos_diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
            ronda = tabla_profesores.loc[uuid_prof]['ronda']
            #
            f.write('<div><h3 id="' + uuid_prof + '">' +
                    '{:d}. '.format(iprof) +
                    tabla_profesores.loc[uuid_prof]['nombre'] + ' ' +
                    tabla_profesores.loc[uuid_prof]['apellidos'] +
                    '</h3>\n')
            #
            f.write('<font face="Courier">')
            f.write('<strong>Encargo docente...: </strong><pre>')
            f.write('{0:9.4f}</pre></font><br>\n'.format(creditos_encargo))
            #
            f.write('<font face="Courier">')
            f.write('<strong>Créditos asignados: </strong><pre>')
            f.write('{0:9.4f}</pre></font><br>\n'.format(creditos_asignados))
            #
            if creditos_diferencia == 0:
                color = '#000'
            elif creditos_diferencia < 0:
                color = '#a00'
            else:
                color = '#0a0'
            f.write('<font face="Courier">')
            f.write('<strong>Diferencia........: </strong><pre>')
            f.write('<font color="' + color + '">')
            f.write('{0:9.4f}</font></pre></font><br>\n'.format(
                creditos_diferencia))
            #
            f.write('<font face="Courier">')
            f.write('<strong>Siguiente ronda...: </strong><pre>')
            f.write('{0:4d}</pre></font><br><br>\n'.format(ronda))
            # subset of bitacora for the selected teacher
            seleccion = bitacora.loc[
                (bitacora['uuid_prof'] == uuid_prof) &
                (bitacora['date_removed'] == 'None') &
                (bitacora['uuid_titu'] != NULL_UUID)
                ].copy()
            # find how many times the selected teacher appears
            ntimes = seleccion.shape[0]
            if ntimes == 0:
                f.write('<p>No tiene docencia asignada</p>\n')
            else:
                f.write('''
<table id="tabla_asignacion">

<thead>
<tr style="text-align: left;">
<th>Curso</th>
<th style="text-align: center;">Semestre</th>
<th style="text-align: center;">Código</th>
<th style="text-align: center;">Ronda</th>
<th>Asignatura</th>
<th>Área</th>
<th style="text-align: center;">Créditos<br>iniciales</th>
<th>Comentarios</th>
<th style="text-align: center;">Grupo</th>
<th style="text-align: center;">Créditos<br>elegidos</th>
</tr>
</thead>

<tbody>

''')
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
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['round_added'].tolist()[i]
                    ))
                    f.write('<td>{}</td>\n'.format(
                        seleccion['asignatura'].tolist()[i]
                    ))
                    f.write('<td>{}</td>\n'.format(
                        seleccion['area'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">' +
                            '{0:9.4f}</td>\n'.format(
                                seleccion['creditos_iniciales'].tolist()[i]
                            ))
                    f.write('<td>{}</td>\n'.format(
                        seleccion['comentarios'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['grupo'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">' +
                            '{0:9.4f}</td>\n'.format(
                                seleccion['creditos_elegidos'].tolist()[i]
                            ))
                f.write('\n</tbody>\n\n')
                #
                f.write('<tfoot>\n\n')
                f.write('<tr>\n')
                f.write('<td colspan="9" style="text-align: right;">SUMA</td>')
                creditos = seleccion['creditos_elegidos'].sum()
                f.write('<td style="text-align: center; font-weight: bold; ' +
                        'background-color: ' + COLOR_ASIGNACION_HEAD +
                        '; color: white;">' +
                        '{0:9.4f}'.format(creditos) + '</td>\n')
                f.write('</tr>\n')
                #
                f.write('\n</tfoot>\n\n')
                f.write('</table>\n\n')

            f.write('<p><a href="index.html">Volver a la página principal</a></p>\n')
            f.write('<hr class="sep"></div>\n\n')

        f.write(date_last_update())
        f.write('</body>\n\n</html>\n')
        f.close()
