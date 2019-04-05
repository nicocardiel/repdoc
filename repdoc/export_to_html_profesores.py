from .date_last_update import date_last_update

from .define_gui_layout import COLOR_PROFESORES


def export_to_html_profesores(tabla_profesores, bitacora):
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
    border: 1px solid #ddd;
    padding: 8px;
  }
  
  #tabla_profesores tr:nth-child(even) {
    background-color: #f2f2f2;
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
    background-color: ''' + COLOR_PROFESORES + ''';
    color: white;
  }
  
  </style>
</head>

<body>

''')

    f.write('''
<h1>Reparto Docente FTA, curso 2019-2020</h1> 
<h2>Listado de profesores</h2>
''')

    f.write('''
<table id="tabla_profesores">

<thead>
<tr style="text-align: left;">
<th>Apellidos</th>
<th>Nombre</th>
<th>Categoría</th>
<th>Encargo docente</th>
<th>Créditos asignados</th>
<th>Diferencia</th>
</tr>
</thead>

<tbody>

''')

    for uuid_prof in tabla_profesores.index:
        f.write('\n<tr>\n')
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
        f.write('<td>' +
                tabla_profesores.loc[uuid_prof]['categoria'] +
                '</td>\n')
        #
        creditos = tabla_profesores.loc[uuid_prof]['encargo']
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        #
        creditos = tabla_profesores.loc[uuid_prof]['asignados']
        f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        #
        creditos = tabla_profesores.loc[uuid_prof]['diferencia']
        if creditos == 0:
            color = '#000'
        elif creditos < 0:
            color = '#a00'
        else:
            color = '#0a0'
        f.write('<td style="text-align: right; color:' + color + ';">' +
                '{0:9.4f}'.format(creditos) + '</td>\n</tr>\n')
    f.write('\n</tbody>\n\n')
    #
    f.write('<tfoot>\n\n')
    f.write('<tr>\n')
    f.write('<td colspan="3" style="text-align: right;">SUMA</td>')
    creditos = tabla_profesores['encargo'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_PROFESORES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_profesores['asignados'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_PROFESORES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_profesores['diferencia'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_PROFESORES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    f.write('</tr>\n')
    #
    f.write('\n</tfoot>\n\n</table>\n\n')
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
    border: 1px solid #ddd;
    padding: 8px;
  }
  
  #tabla_asignacion tr:nth-child(even) {
    background-color: #f2f2f2;
  }
  
  #tabla_asignacion tr:hover {
    background-color: #ddd;
  }
  
  #tabla_asignacion th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: #4C50AF;
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
    border: 3px solid #4C50AF;
  }

  </style>
</head>

<body>

''')

        f.write('''
<h1>Reparto Docente FTA, curso 2019-2020</h1> 
<h2>Asignación de asignaturas por profesor</h2>
''')

        for uuid_prof in tabla_profesores.index:
            f.write('<div><h3 id="' + uuid_prof + '">' +
                    tabla_profesores.loc[uuid_prof]['nombre'] + ' ' +
                    tabla_profesores.loc[uuid_prof]['apellidos'] +
                    '</h3>\n')
            creditos = tabla_profesores.loc[uuid_prof]['encargo']
            f.write('<font face="Courier">')
            f.write('<strong>Encargo docente...: </strong><pre>')
            f.write('{0:9.4f}</pre></font><br>\n'.format(creditos))
            creditos = tabla_profesores.loc[uuid_prof]['asignados']
            f.write('<font face="Courier">')
            f.write('<strong>Créditos asignados: </strong><pre>')
            f.write('{0:9.4f}</pre></font><br>\n'.format(creditos))
            creditos = tabla_profesores.loc[uuid_prof]['diferencia']
            if creditos == 0:
                color = '#000'
            elif creditos < 0:
                color = '#a00'
            else:
                color = '#0a0'
            f.write('<font face="Courier">')
            f.write('<strong>Diferencia........: </strong><pre>')
            f.write('<font color="' + color + '">')
            f.write('{0:9.4f}</font></pre></font><br><br>\n'.format(creditos))
            # subset of bitacora for the selected teacher
            seleccion = bitacora.loc[
                (bitacora['uuid_prof'] == uuid_prof) &
                (bitacora['date_removed'] == 'None')
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
<th>Semestre</th>
<th>Código</th>
<th>Asignatura</th>
<th>Área</th>
<th>Créditos iniciales</th>
<th>Comentarios</th>
<th>Grupo</th>
<th>Créditos elegidos</th>
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
                    f.write('<td>{}</td>\n'.format(
                        seleccion['asignatura'].tolist()[i]
                    ))
                    f.write('<td>{}</td>\n'.format(
                        seleccion['area'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['creditos_iniciales'].tolist()[i]
                    ))
                    f.write('<td>{}</td>\n'.format(
                        seleccion['comentarios'].tolist()[i]
                    ))
                    f.write('<td style="text-align: center;">{}</td>\n'.format(
                        seleccion['grupo'].tolist()[i]
                    ))
                    f.write('<td style="text-align: right;">' +
                            '{0:9.4f}</td>\n'.format(
                                seleccion['creditos_elegidos'].tolist()[i]
                            ))
                f.write('\n</tbody>\n\n')
                #
                f.write('<tfoot>\n\n')
                f.write('<tr>\n')
                f.write('<td colspan="8" style="text-align: right;">SUMA</td>')
                creditos = seleccion['creditos_elegidos'].sum()
                f.write('<td style="text-align: right; font-weight: bold; ' +
                        'background-color: #4C50AF; color: white;">' +
                        '{0:9.4f}'.format(creditos) + '</td>\n')
                f.write('</tr>\n')
                #
                f.write('\n<tfoot>\n\n')
                f.write('</table>\n\n')

            f.write('<hr class="sep"></div>\n\n')

        f.write(date_last_update())
        f.write('</body>\n\n</html>\n')
        f.close()
