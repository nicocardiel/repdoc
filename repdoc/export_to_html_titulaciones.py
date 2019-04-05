from .date_last_update import date_last_update

from .define_gui_layout import COLOR_NO_DISPONIBLE
from .define_gui_layout import COLOR_TITULACIONES


def export_to_html_titulaciones(tabla_titulaciones):
    """Export to html tabla_titulaciones

    """

    f = open('repdoc_titulaciones.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>FTA, 2019-2020</title>

  <style>

  p, h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
  }
  
  #tabla_titulaciones {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
  }

  #tabla_titulaciones td, #tabla_titulaciones th {
    border: 1px solid #ddd;
    padding: 8px;
  }

  #tabla_titulaciones tr:nth-child(even) {
    background-color: #f2f2f2;
  }

  #tabla_titulaciones tr:hover {
    background-color: #ddd;
  }

  #tabla_titulaciones th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_TITULACIONES + ''';
    color: white;
  }

  </style>
</head>

<body>

''')

    f.write('''
<h1>Reparto Docente FTA, curso 2019-2020</h1> 
<p></p>
<p>Enlace a tabla resumen de 
<a href="repdoc_profesores.html">Profesores</a></p>
<p></p>
<p>Enlace a tabla de 
<a href="repdoc_asignacion.html">asignación de asignaturas</a></p>
<p></p>
<p>Enlace al
<a href="repdoc_bitacora.html">cuaderno de bitácora</a>
del reparto docente</p>
<p></p>
<h2>Tabla resumen de titulaciones</h2>
''')

    f.write('''
<table id="tabla_titulaciones">

<thead>
<tr style="text-align: left;">
<th>Titulación</th>
<th>Créditos iniciales</th>
<th>Créditos elegidos</th>
<th>Créditos disponibles</th>
<th>Créditos para Bec./Col.</th>
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
    f.write('<td colspan="1" style="text-align: right;">SUMA</td>\n')
    creditos = tabla_titulaciones['creditos_iniciales'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_titulaciones['creditos_elegidos'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_titulaciones['creditos_disponibles'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')
    creditos = tabla_titulaciones['creditos_beccol'].sum()
    f.write('<td style="text-align: right; font-weight: bold; ' +
            'background-color: ' + COLOR_TITULACIONES + '; color: white;">' +
            '{0:9.4f}'.format(creditos) + '</td>\n')

    f.write('\n</tfoot>\n\n')
    #
    f.write('\n</table>\n\n')
    f.write(date_last_update())
    f.write('</body>\n\n</html>\n')
    f.close()
