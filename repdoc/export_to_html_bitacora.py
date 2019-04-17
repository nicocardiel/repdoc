from .date_last_update import date_last_update

from .define_gui_layout import COLOR_BITACORA_HEAD
from .define_gui_layout import COLOR_BITACORA_EVEN
from .define_gui_layout import COLOR_BITACORA_ODD
from .define_gui_layout import COLOR_NO_DISPONIBLE


def export_to_html_bitacora(bitacora):
    """Export bitacora to html and xlsx files

    """

    bitacora.to_excel('repdoc_bitacora.xlsx', header=True)

    bitacora.to_html('repdoc_bitacora_raw.html')

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
<h1>Reparto Docente FTA, curso 2019-2020</h1> 
<h2>Cuaderno de bitácora</h2>
''')

    f.write('''
<table id="tabla_bitacora">

<thead>
<tr style="text-align: left;">
''')

    f.write('<th>uuid_bita</th>\n')
    for colname in bitacora.columns.tolist():
        f.write('<th>' + colname + '</th>\n')

    f.write('''
</tr>
</thead>

<tbody>

''')

    for uuid_bita in bitacora.index:
        status = str(bitacora.loc[uuid_bita]['date_removed']) == 'None'
        if status:
            f.write('\n<tr>\n')
        else:
            f.write(
                '\n<tr style="background: ' + COLOR_NO_DISPONIBLE + ';">\n'
            )
        f.write('<td>{}</td>\n'.format(uuid_bita))
        for colname in bitacora.columns.tolist():
            f.write('<td>{}</td>\n'.format(
                bitacora.loc[uuid_bita][colname]
            ))
        f.write('</tr>\n')

    f.write('\n</tbody>\n\n')
    f.write('\n</table>\n\n')

    f.write(date_last_update())
    f.write('</body>\n\n</html>\n')
    f.close()
