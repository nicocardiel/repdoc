from .date_last_update import date_last_update

from .define_gui_layout import COLOR_ASIGNATURAS_HEAD
from .define_gui_layout import COLOR_ASIGNATURAS_EVEN
from .define_gui_layout import COLOR_ASIGNATURAS_ODD
from .define_gui_layout import COLOR_NO_DISPONIBLE


def export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas):
    """Export to html bigdict_tablas_asignaturas

    """

    for i, key in enumerate(bigdict_tablas_asignaturas.keys()):
        tabla_asignaturas = bigdict_tablas_asignaturas[key]
        #
        f = open('repdoc_titulacion_{:02d}.html'.format(i + 1), 'wt')
        f.write('''
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

        f.write('''
<h1>Reparto Docente FTA, curso 2019-2020</h1> 
<h2>Listado de asignaturas: {}</h2>
'''.format(key))

        f.write('''
<table id="tabla_asignaturas">

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
<th>Bec./Col.</th>
<th>Profesor anterior</th>
<th>Antigüedad</th>
<th>Profesor próximo curso</th>
<th>Créditos disponibles</th>
</tr>
</thead>

<tbody>

''')

        def insert_separator():
            for idum in range(2):
                f.write('\n<tr style="background: ' +
                        COLOR_ASIGNATURAS_HEAD +
                        '; height: 2px; padding-top: 0px; ' +
                        'padding-bottom: 0px;">')
                f.write('<td colspan="13" style="height: 2px; ' +
                        'padding-top: 0px; padding-bottom: 0px;">' +
                        '</td></tr>\n')

        ultima_asignatura = None
        for uuid_asig in tabla_asignaturas.index:
            nueva_asignatura = tabla_asignaturas.loc[uuid_asig]['asignatura']
            if ultima_asignatura is None:
                ultima_asignatura = nueva_asignatura
            else:
                if nueva_asignatura != ultima_asignatura:
                    insert_separator()
                    ultima_asignatura = nueva_asignatura
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_disponibles']
            if creditos > 0:
                f.write('\n<tr>\n')
            else:
                f.write(
                    '\n<tr style="background: ' + COLOR_NO_DISPONIBLE + ';">\n'
                )
            f.write('<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['curso']
            ))
            f.write('<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['semestre']
            ))
            f.write('<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['codigo']
            ))
            f.write('<td>{}</td>\n'.format(nueva_asignatura))
            f.write('<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['area']
            ))
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_iniciales']
            f.write('<td style="text-align: right;">' +
                    '{0:9.4f}'.format(creditos) + '</td>\n')
            f.write('<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['comentarios']
            ))
            f.write('<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['grupo']
            ))
            f.write('<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['bec_col']
            ))
            f.write('<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['profesor_anterior']
            ))
            f.write('<td style="text-align: center;">{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['antiguedad']
            ))
            f.write('<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['nuevo_profesor']
            ))
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_disponibles']
            f.write('<td style="text-align: right;">' +
                    '{0:9.4f}'.format(creditos) + '</td>\n'
                    )
            f.write('</tr>\n')

        insert_separator()
        f.write('\n</tbody>\n\n')
        #
        f.write('<tfoot>\n\n')
        f.write('<tr>\n')
        f.write('<td colspan="5" style="text-align: right;">SUMA</td>\n')
        creditos = tabla_asignaturas['creditos_iniciales'].sum()
        f.write('<td style="text-align: right; font-weight: bold; ' +
                'background-color: ' + COLOR_ASIGNATURAS_HEAD +
                '; color: white;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        f.write('<td colspan="6" style="text-align: right;">SUMA</td>\n')
        creditos = tabla_asignaturas['creditos_disponibles'].sum()
        f.write('<td style="text-align: right; font-weight: bold; ' +
                'background-color: ' + COLOR_ASIGNATURAS_HEAD +
                '; color: white;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        f.write('\n</tfoot>\n\n')
        #
        f.write('\n</table>\n\n')
        f.write(date_last_update())
        f.write('</body>\n\n</html>\n')
        f.close()
