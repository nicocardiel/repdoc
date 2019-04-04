import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import sys
from uuid import uuid4


WIDTH_HLINE = 90
WIDTH_HLINE_SUMMARY = 62
WIDTH_TEXT_SUMMARY = 18
WIDTH_TEXT_LABEL = 18
WIDTH_TEXT_UUID = 30
WIDTH_INPUT_COMBO = 50
WIDTH_INPUT_NUMBER = 10
WIDTH_INPUT_COMMENT = 50
WIDTH_SPACES_FOR_UUID = 150

COLOR_TITULACIONES = '#AF4CAF'
COLOR_ASIGNATURAS = '#AF4C50'
COLOR_PROFESORES = '#4CAF50'
COLOR_NO_DISPONIBLE = '#555'


def new_uuid(megalist_uuid):
    """Return new uuid after checking that there is no collision.

    """

    loop = True

    while loop:
        newvalue = str(uuid4())
        newlist = megalist_uuid + [newvalue]
        if len(newlist) != len(set(newlist)):
            print('UUID collision with:' + newvalue)
        else:
            return newvalue


def str_nonan(s):
    """Avoid NaN due to empty strings: return single space instead.

    """

    if len(s) > 0:
        return s
    else:
        return ' '


def fill_cell_with_previous_value(s):
    """Return list removing NaN in Series

    """

    ll = len(s)
    result = []
    i = 0
    last = None
    while i < ll:
        if type(s[i]) is str:
            last = s[i]
            result.append(last)
        else:
            if np.isnan(s[i]):
                if last is None:
                    raise ValueError('Unexpected error')
                else:
                    result.append(last)
            else:
                last = s[i]
                result.append(last)
        i += 1

    return result


def read_tabla_titulaciones(xlsxfilename, course, debug=False):
    """Lee hoja Excel con lista de titulaciones.

    """

    if course == '2019-2020':
        sheet_name = 'Resumen Encargo'
        skiprows = 4
        usecols = [1, 2]
        names = ['uuid_titu', 'titulacion']
        converters = {'uuid_titu': str, 'titulacion': str}
    else:
        print('Course: ' + course)
        raise ValueError('Unexpected course!')

    if debug:
        print('Reading ' + xlsxfilename)
        print('-> Sheet: "' + sheet_name + '"')

    tabla_inicial = pd.read_excel(
        xlsxfilename,
        sheet_name=sheet_name,
        skiprows=skiprows,
        header=None,
        usecols=usecols,
        names=names,
        converters=converters
    )

    # remove unnecessary rows
    lok = tabla_inicial['uuid_titu'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_titulaciones = tabla_inicial.copy()
    tabla_titulaciones.index = tabla_inicial['uuid_titu']
    del tabla_titulaciones['uuid_titu']

    # check that uuid's are unique
    if len(tabla_titulaciones.index) != len(set(tabla_titulaciones.index)):
        raise ValueError('UUIDs are not unique!')

    if debug:
        print(tabla_titulaciones)
        input('Press <CR> to continue...')

    return tabla_titulaciones


def read_tabla_asignaturas(xlsxfilename, course, sheet_name, debug=False):
    """Lee hoja Excel con lista de asignaturas

    """

    if course == '2019-2020':
        skiprows = 5
        usecols = range(1, 13)
        names = ['curso', 'semestre', 'codigo', 'asignatura', 'area',
                 'uuid_asig', 'creditos_iniciales', 'comentarios',
                 'grupo', 'bec_col', 'profesor_anterior', 'antiguedad'
                 ]
        converters = {'curso': str, 'semestre': int, 'codigo': int,
                      'area': str, 'uuid_asig': str,
                      'creditos_iniciales': float, 'comentarios': str_nonan,
                      'grupo': str_nonan, 'bec_col': int,
                      'profesor_anterior': str_nonan, 'antiguedad': int
                      }
    else:
        print('Course: ' + course)
        raise ValueError('Unexpected course!')

    if debug:
        print('Reading ' + xlsxfilename)
        print('-> Sheet: "' + sheet_name + '"')

    tabla_inicial = pd.read_excel(
        xlsxfilename,
        sheet_name=sheet_name,
        skiprows=skiprows,
        header=None,
        usecols=usecols,
        names=names,
        converters=converters
    )

    # remove unnecessary rows
    lok = tabla_inicial['uuid_asig'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # fill empty cells
    for item in ['curso', 'semestre', 'codigo', 'asignatura']:
        tabla_inicial[item] = \
            fill_cell_with_previous_value(tabla_inicial[item])

    # use uuid as index
    tabla_asignaturas = tabla_inicial.copy()
    tabla_asignaturas.index = tabla_inicial['uuid_asig']
    del tabla_asignaturas['uuid_asig']

    # check that uuid's are unique
    if len(tabla_asignaturas.index) != len(set(tabla_asignaturas.index)):
        raise ValueError('UUIDs are not unique!')

    if debug:
        print(tabla_asignaturas)
        print('Créditos totales:',
              round(tabla_asignaturas['creditos_iniciales'].sum(), 3))
        sumproduct = tabla_asignaturas['creditos_iniciales'] * \
                     tabla_asignaturas['bec_col']
        print('Créditos posibles para becarios/colaboradores:',
              round(sumproduct.sum(), 3))
        input("Press <CR> to continue...")

    return tabla_asignaturas


def read_tabla_profesores(xlsxfilename, course, debug=False):
    """Lee hoja Excel con lista de profesores que participan en rondas

    """

    if course == '2019-2020':
        sheet_name = 'Asignación'
        skiprows = 7
        usecols = [0, 1, 2, 3, 18]
        names = ['uuid_prof', 'apellidos', 'nombre', 'categoria',
                 'encargo']
        converters = {'uuid_prof': str,
                      'apellidos': str,
                      'nombre': str,
                      'categoria': str,
                      'encargo': float}
    else:
        print('Course: ' + course)
        raise ValueError('Unexpected course!')

    if debug:
        print('Reading ' + xlsxfilename)
        print('-> Sheet: "' + sheet_name + '"')

    tabla_inicial = pd.read_excel(
        xlsxfilename,
        sheet_name=sheet_name,
        skiprows=skiprows,
        header=None,
        usecols=usecols,
        names=names,
        converters=converters
    )

    # remove unnecessary rows
    lok = tabla_inicial['uuid_prof'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_profesores = tabla_inicial.copy()
    tabla_profesores.index = tabla_inicial['uuid_prof']
    del tabla_profesores['uuid_prof']

    # check that uuid's are unique
    if len(tabla_profesores.index) != len(set(tabla_profesores.index)):
        raise ValueError('UUIDs are not unique!')

    if debug:
        print(tabla_profesores)
        print('Encargo total:', tabla_profesores['encargo'].sum())
        input('Press <CR> to continue...')

    return tabla_profesores


def display_in_terminal(event, values):
    """Show 'event' and 'values' in the terminal

    """

    print("\nEvent: '" + event + "'")
    for key in values:
        output = "    '" + key + "': "
        if isinstance(values[key], str):
            if values[key][-46:-42] == 'uuid':
                output += "'" + values[key][:-46].rstrip() + " ... " + \
                          values[key][-46:] + "'"
            else:
                output += "'" + values[key] + "'"
        else:
            output += str(values[key])
        print(output)


def define_layout(fontsize, num_titulaciones):
    """Define GUI layout

    """

    # define monospaced typeface for results
    fontname_header = 'courier bold'
    fontname_no = 'courier'

    layout = [[sg.Text('Titulación',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('iniciales',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('elegidos',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('disponibles',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('Bec./Col.',
                       font=(fontname_header, fontsize),
                       text_color='#33aa33',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center')]]
    for i in range(num_titulaciones):
        clabel = '_{:02d}_'.format(i + 1)
        newrow = [sg.Text('undefined', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_titulacion' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_total' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                       size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                       key='_summary_elegidos' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_disponibles' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_beccol' + clabel)
                  ]
        layout += [newrow]
    #layout += [[sg.Text('-' * WIDTH_HLINE_SUMMARY, font=fontname)]]
    layout += [[sg.Text('TOTAL', text_color='#3333ff',
                        font=(fontname_header, fontsize),
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#3333ff',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_total_'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#3333ff',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_elegidos_'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#3333ff',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_disponibles_'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#33aa33',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_beccol_')
                ]]
    layout += [[sg.Checkbox('Excluir elección de asignaturas para '
                            'Becarios/Colaboradores',
                           default=False,
                           change_submits=True,
                           auto_size_text=True,
                           key='_excluir_asignaturas_beccol_')],
               # ---
               [sg.Text('_' * WIDTH_HLINE)],
               # ---
               [sg.Checkbox('Excluir docentes RyC y asimilados',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_excluir_RyC_'),
                sg.Checkbox('Excluir Becarios/Colaboradores',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_excluir_colaboradores_')],
               # ---
               [sg.Text('Nº umbral de créditos:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_umbral_creditos_'),
                sg.InputText(default_text='0.0',
                             size=(WIDTH_INPUT_NUMBER, 1),
                             justification='left',
                             do_not_clear=True, disabled=False,
                             key='_umbral_creditos_'),
                sg.Button('Establecer umbral', key='_establecer_umbral_'),
                sg.Text('(0: selecciona todos los profesores)',
                        text_color='#aaaaaa',
                        auto_size_text=True)],
               # ---
               [sg.Text('_' * WIDTH_HLINE)],
               # ---
               [sg.Text('Nº de profesores seleccionados:',
                        text_color='#aaaaaa', auto_size_text=True),
                sg.Text('0', text_color='#aaaaaa', auto_size_text=True,
                        key='_num_prof_seleccionados_')],
               # ---
               [sg.Text('Profesor/a:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_profesor_'),
                sg.InputCombo(values=['---'],
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              disabled=True, key='_profesor_')],
               # ---
               [sg.Text('Encargo docente:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_encargo_prof_'),
                sg.Text('---', key='_encargo_prof_',
                        size=(WIDTH_TEXT_LABEL, 1))],
               # ---
               [sg.Text('Créditos asignados:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_asignados_prof_'),
                sg.Text('---', key='_asignados_prof_',
                        size=(WIDTH_TEXT_LABEL, 1))],
               # ---
               [sg.Text('Diferencia:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_diferencia_prof_'),
                sg.Text('---', key='_diferencia_prof_',
                        size=(WIDTH_TEXT_LABEL, 1))],
               # ---
               [sg.Text('Docencia asignada:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_docencia_asignada_'),
                sg.InputCombo(values=['---'], disabled=True,
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              key='_docencia_asignada_')],
               # ---
               [sg.Button('Continuar', disabled=True, key='_continuar_'),
                sg.Button('Eliminar', disabled=True, key='_eliminar_')],
               [sg.Text('_' * WIDTH_HLINE)],
               # ---
               [sg.Text('Titulación:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_titulacion_'),
                sg.InputCombo(values=['---'], disabled=True,
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              key='_titulacion_')],
               # ---
               [sg.Text('Asignatura elegida:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right',
                        key='_label_asignatura_elegida_'),
                sg.InputCombo(values=['---'], disabled=True,
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              key='_asignatura_elegida_')],
               # ---
               [sg.Text('', size=(WIDTH_TEXT_LABEL, 1)),
                sg.Checkbox('Todos los créditos',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_fraccion_todo_',
                            disabled=True),
                sg.Checkbox('Solo una parte',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_fraccion_parte_',
                            disabled=True),
                sg.Text('Créditos a elegir:', text_color="#aaaaaa",
                        auto_size_text=True,
                        key='_label_creditos_elegidos_'),
                sg.InputText(default_text='0.0', text_color="#aaaaaa",
                             size=(WIDTH_INPUT_NUMBER, 1),
                             justification='left',
                             do_not_clear=True, disabled=True,
                             key='_creditos_elegidos_')],
               # ---
               [sg.Text('Explicación:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right',
                        key='_label_explicacion_'),
                sg.InputText(default_text=' ',
                             size=(WIDTH_INPUT_COMMENT, 1),
                             justification='left',
                             do_not_clear=True, disabled=True,
                             key='_explicacion_')],
               # ---
               [sg.Button('Aplicar', disabled=True, key='_aplicar_'),
                sg.Button('Cancelar', disabled=True, key='_cancelar_')],
               [sg.Text('_' * WIDTH_HLINE)],
               [sg.Button('Salir', key='_salir_')]
               ]

    return layout


def filtra_titulaciones(tabla_titulaciones):
    """Return list with degrees with available credits.

    """

    num_titulaciones = tabla_titulaciones.shape[0]
    lista_titulaciones = []
    for i in range(num_titulaciones):
        if tabla_titulaciones['creditos_disponibles'][i] > 0:
            nombre_titulacion = tabla_titulaciones['titulacion'][i]
            ldum = len(nombre_titulacion)
            if ldum < WIDTH_SPACES_FOR_UUID:
                nombre_titulacion += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
            nombre_titulacion += ' uuid_titu=' + tabla_titulaciones.index[i]
            lista_titulaciones.append(nombre_titulacion)

    return lista_titulaciones


def filtra_asignaturas(tabla_asignaturas,
                       excluir_asignaturas_beccol=False):
    """Return list with subjects with available credits.

    """

    num_asignaturas = tabla_asignaturas.shape[0]
    lista_asignaturas = []
    for i in range(num_asignaturas):
        if excluir_asignaturas_beccol:
            if tabla_asignaturas['bec_col'][i] == 1:
                incluir_asignatura = False
            else:
                incluir_asignatura = True
        else:
            incluir_asignatura = True
        if incluir_asignatura:
            if tabla_asignaturas['creditos_disponibles'][i] > 0:
                dumtxt = '[' + tabla_asignaturas['curso'][i] + '] '
                dumtxt += tabla_asignaturas['asignatura'][i] + ', '
                dumtxt += str(
                    round(tabla_asignaturas['creditos_disponibles'][i], 4)
                ) + ' créditos'
                if tabla_asignaturas['comentarios'][i] != ' ':
                    dumtxt += ', ' + tabla_asignaturas['comentarios'][i]
                if tabla_asignaturas['grupo'][i] != ' ':
                    dumtxt += ', grupo ' + tabla_asignaturas['grupo'][i]
                ldum = len(dumtxt)
                if ldum < WIDTH_SPACES_FOR_UUID:
                    dumtxt += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                dumtxt += ' uuid_asig=' + tabla_asignaturas.index[i]
                lista_asignaturas.append(dumtxt)

    return lista_asignaturas


def filtra_seleccion_del_profesor(uuid_prof, bitacora):
    """Return list with subjects already assigned to a teacher.

    """

    output = ['---']

    # subset of bitacora for the selected teacher
    seleccion = bitacora.loc[
        (bitacora['uuid_prof'] == uuid_prof) &
        (bitacora['date_removed'] == 'None')
    ].copy()

    # find how many times the selected teacher appears
    ntimes = seleccion.shape[0]
    if ntimes == 0:
        return output

    for i in range(ntimes):
        dumtxt = '[' + seleccion['curso'].tolist()[i] + '] '
        dumtxt += seleccion['asignatura'].tolist()[i] + ', '
        dumtxt += str(
            round(seleccion['creditos_elegidos'].tolist()[i], 4)
        ) + ' créditos'
        if seleccion['comentarios'].tolist()[i] != ' ':
            dumtxt += ', ' + seleccion['comentarios'].tolist()[i]
        if seleccion['grupo'].tolist()[i] != ' ':
            dumtxt += ', grupo ' + seleccion['grupo'].tolist()[i]
        ldum = len(dumtxt)
        if ldum < WIDTH_SPACES_FOR_UUID:
            dumtxt += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
        dumtxt += ' uuid_bita=' + seleccion.index.tolist()[i]
        output.append(dumtxt)

    return output


def date_last_update():
    """Return current date

    """

    return '\n\n<br><br>Last update: ' + str(datetime.now()) + '\n\n'


def export_to_html_titulaciones(tabla_titulaciones):
    """Export to html tabla_titulaciones

    """

    f = open('repdoc_titulaciones.html', 'wt')
    f.write('''
<!DOCTYPE html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>Tabla de titulaciones</title>

  <style>

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
  <title>Tabla de asignaturas</title>

  <style>

  #tabla_asignaturas {
    font-family: Arial, Helvetica, sans-serif;
    border-collapse: collapse;
  }

  #tabla_asignaturas td, #tabla_asignaturas th {
    border: 1px solid #ddd;
    padding: 8px;
  }

  #tabla_asignaturas tr:nth-child(even) {
    background-color: #f2f2f2;
  }

  #tabla_asignaturas tr:hover {
    background-color: #ddd;
  }

  #tabla_asignaturas th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: ''' + COLOR_ASIGNATURAS + ''';
    color: white;
  }

  </style>
</head>

<body>

''')

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
<th>Créditos disponibles</th>
</tr>
</thead>

<tbody>

''')
        for uuid_asig in tabla_asignaturas.index:
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
            f.write('<td>{}</td>\n'.format(
                tabla_asignaturas.loc[uuid_asig]['asignatura']
            ))
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
            creditos = tabla_asignaturas.loc[uuid_asig]['creditos_disponibles']
            f.write('<td style="text-align: right;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
            f.write('</tr>\n')

        f.write('\n</tbody>\n\n')
        #
        f.write('<tfoot>\n\n')
        f.write('<tr>\n')
        f.write('<td colspan="5" style="text-align: right;">SUMA</td>\n')
        creditos = tabla_asignaturas['creditos_iniciales'].sum()
        f.write('<td style="text-align: right; font-weight: bold; ' +
                'background-color: ' + COLOR_ASIGNATURAS +
                '; color: white;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        f.write('<td colspan="5" style="text-align: right;">SUMA</td>\n')
        creditos = tabla_asignaturas['creditos_disponibles'].sum()
        f.write('<td style="text-align: right; font-weight: bold; ' +
                'background-color: ' + COLOR_ASIGNATURAS +
                '; color: white;">' +
                '{0:9.4f}'.format(creditos) + '</td>\n')
        f.write('\n</tfoot>\n\n')
        #
        f.write('\n</table>\n\n')
        f.write(date_last_update())
        f.write('</body>\n\n</html>\n')
        f.close()


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
  <title>Resumen tabla de profesores</title>
  
  <style>
  
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
  <title>Asignación de la docencia</title>
  
  <style>
  
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

        for uuid_prof in tabla_profesores.index:
            f.write('<div><h2 id="' + uuid_prof + '">' +
                    tabla_profesores.loc[uuid_prof]['nombre'] + ' ' +
                    tabla_profesores.loc[uuid_prof]['apellidos'] +
                    '</h2>\n')
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
                f.write('No tiene docencia asignada\n')
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


def export_to_html_bitacora(bitacora):
    """Export bitacora to html and xlsx files

    """

    bitacora.to_html('repdoc_bitacora.html')
    bitacora.to_excel('repdoc_bitacora.xlsx', header=True)


def main(args=None):

    # parse command-line options
    parser = argparse.ArgumentParser(description='Subject assignment tool')

    parser.add_argument("xlsxfile",
                        help="Excel file with input data",
                        type=argparse.FileType())
    parser.add_argument("--bitacora",
                        help="CSV input/output filename",
                        type=argparse.FileType())
    parser.add_argument("--course", required=True,
                        help="Academic course (e.g. 2019-2020)",
                        type=str)
    parser.add_argument("--fontname",
                        help="font name for GUI",
                        default='Helvetica',
                        type=str)
    parser.add_argument("--fontsize",
                        help="font name for GUI",
                        default=12,
                        type=int)
    parser.add_argument("--debug",
                        help="run code in debugging mode",
                        action="store_true")
    parser.add_argument("--echo",
                        help="Display full command line",
                        action="store_true")

    args = parser.parse_args()

    if args.echo:
        print('\033[1m\033[31mExecuting: ' + ' '.join(sys.argv) + '\033[0m\n')

    # ---
    # load Excel sheets

    # variable para almacenar los UUIDs de titulaciones, asignaturas
    # y profesores
    megalist_uuid = []

    # titulaciones
    tabla_titulaciones = read_tabla_titulaciones(
        xlsxfilename=args.xlsxfile.name,
        course=args.course,
        debug=args.debug
    )
    # incluye columnas con créditos iniciales y disponibles
    tabla_titulaciones['creditos_iniciales'] = 0.0
    tabla_titulaciones['creditos_elegidos'] = 0.0
    tabla_titulaciones['creditos_disponibles'] = 0.0
    tabla_titulaciones['creditos_beccol'] = 0.0
    megalist_uuid += tabla_titulaciones.index.tolist()

    # asignaturas de cada titulacion
    bigdict_tablas_asignaturas = {}
    for uuid_titu in tabla_titulaciones.index:
        titulacion = tabla_titulaciones.loc[uuid_titu]['titulacion']
        dumtable = read_tabla_asignaturas(
                xlsxfilename=args.xlsxfile.name,
                course=args.course,
                sheet_name=titulacion,
                debug=args.debug
            )
        # incluye columna con créditos disponibles
        dumtable['creditos_disponibles'] = dumtable['creditos_iniciales']
        bigdict_tablas_asignaturas[titulacion] = dumtable.copy()
        # actualiza número total de créditos disponibles (todas las
        # asignaturas) en tabla de titulaciones
        tabla_titulaciones.loc[uuid_titu, 'creditos_iniciales'] = \
            dumtable['creditos_iniciales'].sum()
        tabla_titulaciones.loc[uuid_titu, 'creditos_disponibles'] = \
            dumtable['creditos_iniciales'].sum()
        sumproduct = dumtable['creditos_disponibles'] * dumtable['bec_col']
        tabla_titulaciones.loc[uuid_titu, 'creditos_beccol'] = \
            sumproduct.sum()
        sumproduct = dumtable['creditos_disponibles'] * dumtable['bec_col']
    # comprueba que los UUIDs son únicos al mezclar todas las asignaturas
    dumlist = []
    for titulacion in tabla_titulaciones['titulacion']:
        dumtable = bigdict_tablas_asignaturas[titulacion]
        dumlist += dumtable.index.tolist()
    if len(dumlist) != len(set(dumlist)):
        for dumuuid in dumlist:
            if dumlist.count(dumuuid) > 1:
                print(dumuuid)
        raise ValueError('UUIDs are not unique when mixing all the subjects!')
    megalist_uuid += dumlist

    # profesores
    tabla_profesores = read_tabla_profesores(
        xlsxfilename=args.xlsxfile.name,
        course=args.course,
        debug=args.debug
    )
    megalist_uuid += tabla_profesores.index.tolist()
    # transforma el encargo de cada profesor de horas a créditos
    tabla_profesores['encargo'] /= 10
    # define columna para almacenar docencia elegida
    tabla_profesores['asignados'] = 0.0
    # define columna para almacenar diferencia entre encargo y eleccion
    tabla_profesores['diferencia'] = tabla_profesores['asignados'] - \
                                     tabla_profesores['encargo']

    # comprueba que los UUIDs de titulaciones, asignaturas y profesores
    # son todos distintos
    if len(megalist_uuid) != len(set(megalist_uuid)):
        for dumuuid in megalist_uuid:
            if megalist_uuid.count(dumuuid) > 1:
                print(dumuuid)
        raise ValueError('UUIDs are not unique when mixing everything!')

    # ---
    # export to HTML files

    export_to_html_titulaciones(tabla_titulaciones)
    export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas)
    export_to_html_profesores(tabla_profesores, bitacora=None)

    # ---
    # define bitacora
    csv_colnames_profesor = ['apellidos', 'nombre', 'categoria']
    csv_colnames_asignatura = ['curso', 'semestre', 'codigo', 'asignatura',
                               'area', 'creditos_iniciales', 'comentarios',
                               'grupo']
    if args.bitacora is None:
        # initialize empty dataframe with the expected columns
        bitacora = pd.DataFrame(
            data=[],
            columns=['uuid_prof', 'uuid_titu', 'uuid_asig',
                     'date_added', 'date_removed',
                     'creditos_elegidos', 'explicacion'] +
                    csv_colnames_profesor + csv_colnames_asignatura
        )
        bitacora.index.name = 'uuid_bita'
        if args.debug:
            print('Initialasing bitacora DataFrame:')
            print(bitacora)
            input('Press <CR> to continue...')
        # export to HTML
        export_to_html_bitacora(bitacora)
    else:
        bitacora = pd.read_excel(args.bitacora.name, index_col=0)
        bitacora.index.name = 'uuid_bita'
        if args.debug:
            print('Initialising bitacora from previous file:')
            print(bitacora)
            input('Press <CR> to continue...')

        for uuid_bita in bitacora.index.tolist():
            # convert NaNs to something else
            non_nan = ['date_removed', 'explicacion', 'comentarios', 'grupo']
            alternative = ['None', ' ', ' ', ' ']
            for item, altnone in zip(non_nan, alternative):
                itemvalue = str(bitacora.loc[uuid_bita][item])
                if itemvalue == 'nan' or itemvalue == 'NaN':
                    bitacora.loc[uuid_bita, item] = altnone
            # apply selected subjects
            status = str(bitacora.loc[uuid_bita]['date_removed']) == 'None'
            if status:
                uuid_prof = bitacora.loc[uuid_bita]['uuid_prof']
                uuid_titu = bitacora.loc[uuid_bita]['uuid_titu']
                uuid_asig = bitacora.loc[uuid_bita]['uuid_asig']
                creditos_elegidos = \
                    bitacora.loc[uuid_bita]['creditos_elegidos']
                asignacion_es_correcta = True
                titulacion = tabla_titulaciones.loc[uuid_titu]['titulacion']
                tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
                if tabla_asignaturas.loc[
                    uuid_asig, 'creditos_disponibles'
                ] >= creditos_elegidos:
                    tabla_asignaturas.loc[
                        uuid_asig, 'creditos_disponibles'
                    ] -= creditos_elegidos
                else:
                    print('¡Créditos disponibles insuficientes!')
                    asignacion_es_correcta = False
                if asignacion_es_correcta:
                    tabla_titulaciones.loc[
                        uuid_titu, 'creditos_disponibles'
                    ] = tabla_asignaturas['creditos_disponibles'].sum()
                    sumproduct = tabla_asignaturas['creditos_disponibles'] * \
                                 tabla_asignaturas['bec_col']
                    tabla_titulaciones.loc[uuid_titu, 'creditos_beccol'] = \
                        sumproduct.sum()
                    tabla_titulaciones.loc[
                        uuid_titu, 'creditos_elegidos'
                    ] = tabla_titulaciones.loc[uuid_titu,
                                               'creditos_iniciales'] - \
                          tabla_titulaciones.loc[uuid_titu,
                                                 'creditos_disponibles']
                    tabla_profesores.loc[
                        uuid_prof, 'asignados'
                    ] += creditos_elegidos
                    tabla_profesores.loc[
                        uuid_prof, 'diferencia'
                    ] = tabla_profesores.loc[uuid_prof, 'asignados'] - \
                        tabla_profesores.loc[uuid_prof, 'encargo']
                else:
                    print('* uuid_bita:', uuid_bita)
                    print('* uuid_prof:', uuid_prof)
                    print('* uuid_titu:', uuid_titu)
                    print('* uuid_asig:', uuid_asig)
                    raise ValueError('Error while processing bitacora!')

        export_to_html_titulaciones(tabla_titulaciones)
        export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas)
        export_to_html_profesores(tabla_profesores, bitacora)

    # ---
    # GUI

    # set global GUI options
    sg.SetOptions(font=(args.fontname, args.fontsize))

    # define GUI layout
    num_titulaciones = tabla_titulaciones.shape[0]
    layout = define_layout(args.fontsize, num_titulaciones)

    # define GUI window
    window = sg.Window('Reparto Docente (FTA), Curso ' +
                       args.course).Layout(layout)

    # ---
    # define auxiliary functions

    def clear_screen_profesor(profesor_disabled=True):
        if profesor_disabled:
            window.Element('_profesor_').Update(values='---', disabled=True)
            window.Element('_num_prof_seleccionados_').Update('0')
        window.Element('_encargo_prof_').Update('---')
        window.Element('_asignados_prof_').Update('---')
        window.Element('_diferencia_prof_').Update('---')
        window.Element('_docencia_asignada_').Update('---')
        window.Element('_titulacion_').Update('---')
        window.Element('_continuar_').Update(disabled=True)
        window.Element('_eliminar_').Update(disabled=True)

    def clear_screen_asignatura():
        window.Element('_titulacion_').Update(values='---', disabled=True)
        window.Element('_asignatura_elegida_').Update(
            values='---',
            disabled=True
        )
        window.Element('_creditos_elegidos_').Update(
            value='0.0',
            disabled=True
        )
        window.Element('_fraccion_todo_').Update(
            value=False, disabled=True
        )
        window.Element('_fraccion_parte_').Update(
            value=False, disabled=True
        )
        window.Element('_explicacion_').Update(value=' ', disabled=True)
        window.Element('_aplicar_').Update(disabled=True)
        window.Element('_cancelar_').Update(disabled=True)

    def update_info_creditos():
        """Update general credit info

        """

        total_iniciales = 0.0
        total_disponibles = 0.0
        total_elegidos = 0.0
        total_disponibles_beccol = 0.0
        cout = '{0:7.3f}'
        num_titulaciones = tabla_titulaciones.shape[0]
        for i in range(num_titulaciones):
            clabel = '_{:02d}_'.format(i + 1)
            uuid_titu = tabla_titulaciones.index[i]
            titulacion = tabla_titulaciones.loc[uuid_titu]['titulacion']
            window.Element('_summary_titulacion' + clabel).Update(titulacion)
            #
            tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
            creditos_iniciales = tabla_asignaturas['creditos_iniciales'].sum()
            window.Element('_summary_total' + clabel).Update(
                cout.format(creditos_iniciales))
            total_iniciales += creditos_iniciales
            creditos_disponibles = tabla_asignaturas[
                'creditos_disponibles'].sum()
            window.Element('_summary_disponibles' + clabel).Update(
                cout.format(creditos_disponibles))
            total_disponibles += creditos_disponibles
            creditos_elegidos = creditos_iniciales - creditos_disponibles
            window.Element('_summary_elegidos' + clabel).Update(
                cout.format(creditos_elegidos))
            total_elegidos += creditos_elegidos
            sumproduct = tabla_asignaturas['creditos_disponibles'] * \
                         tabla_asignaturas['bec_col']
            creditos_disponibles_beccol = sumproduct.sum()
            window.Element('_summary_beccol' + clabel).Update(
                cout.format(creditos_disponibles_beccol))
            total_disponibles_beccol += creditos_disponibles_beccol
        window.Element('_summary_total_').Update(
            value=cout.format(total_iniciales))
        window.Element('_summary_elegidos_').Update(
            value=cout.format(total_elegidos))
        window.Element('_summary_disponibles_').Update(
            value=cout.format(total_disponibles))
        window.Element('_summary_beccol_').Update(
            value=cout.format(total_disponibles_beccol))

    # update initial info
    window.Read(timeout=1)  # for next function to work
    update_info_creditos()

    creditos_max_asignatura = 0.0

    while True:
        event, values = window.Read()
        display_in_terminal(event, values)
        # ---
        if event == '_excluir_asignaturas_beccol_':
            clear_screen_profesor()
            clear_screen_asignatura()
        # ---
        elif event == '_excluir_RyC_':
            clear_screen_asignatura()
            clear_screen_profesor()
        # ---
        elif event == '_excluir_colaboradores_':
            clear_screen_asignatura()
            clear_screen_profesor()
        # ---
        elif event == '_establecer_umbral_':
            lista_profesores = ['---']
            umbral_is_float = True
            umbral = 0.0  # avoid warning
            num_profesores = 0
            try:
                umbral = float(values['_umbral_creditos_'])
            except ValueError:
                sg.Popup('ERROR', 'Número inválido')
                umbral_is_float = False
            if umbral_is_float:
                if umbral < 0:
                    sg.Popup('ERROR',
                             '¡El umbral ha de ser mayor o igual que cero!')
                    window.Element('_umbral_creditos_').Update('0.0')
                else:
                    window.Element('_umbral_creditos_').Update(
                        str(float(umbral))
                    )
                    for i in range(tabla_profesores.shape[0]):
                        incluir_profesor = True
                        if values['_excluir_RyC_']:
                            if 'RyC' in tabla_profesores['categoria'][i]:
                                incluir_profesor = False
                        if values['_excluir_colaboradores_']:
                            if tabla_profesores['categoria'][i] == \
                                'Colaborador':
                                incluir_profesor = False
                        if incluir_profesor:
                            nombre_completo = tabla_profesores['nombre'][i] +\
                                              ' ' +\
                                              tabla_profesores['apellidos'][i]
                            ldum = len(nombre_completo)
                            if ldum < WIDTH_SPACES_FOR_UUID:
                                nombre_completo += \
                                    (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                            nombre_completo += ' uuid_prof=' + \
                                               tabla_profesores.index[i]
                            if umbral == 0:
                                num_profesores += 1
                                lista_profesores.append(nombre_completo)
                            elif tabla_profesores['asignados'][i] < umbral:
                                num_profesores += 1
                                lista_profesores.append(nombre_completo)
            clear_screen_profesor()
            window.Element('_num_prof_seleccionados_').Update(
                str(num_profesores)
            )
            window.Element('_profesor_').Update(
                values=lista_profesores,
                disabled=False
            )
            clear_screen_asignatura()
        # ---
        elif event == '_profesor_':
            if values['_profesor_'] == '---':
                clear_screen_profesor(profesor_disabled=False)
            else:
                uuid_prof = values['_profesor_'][-36:]
                encargo = tabla_profesores.loc[uuid_prof]['encargo']
                asignados = tabla_profesores.loc[uuid_prof]['asignados']
                diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(round(diferencia, 4))
                seleccion_del_profesor = filtra_seleccion_del_profesor(
                    uuid_prof, bitacora
                )
                if len(seleccion_del_profesor) > 1:
                    window.Element('_docencia_asignada_').Update(
                        values=seleccion_del_profesor,
                        disabled=False
                    )
                else:
                    window.Element('_docencia_asignada_').Update(
                        values=['---'],
                        disabled=True
                    )
                window.Element('_continuar_').Update(disabled=False)
        # ---
        elif event == '_docencia_asignada_':
            if values['_docencia_asignada_'] == '---':
                window.Element('_eliminar_').Update(disabled=True)
            else:
                window.Element('_eliminar_').Update(disabled=False)
        # ---
        elif event == '_continuar_':
            uuid_prof = values['_profesor_'][-36:]
            if uuid_prof is None:
                raise ValueError('Unexpected uuid_prof == None')
            window.Element('_profesor_').Update(disabled=True)
            window.Element('_docencia_asignada_').Update(
                values=['---'],
                disabled=True
            )
            window.Element('_continuar_').Update(disabled=True)
            window.Element('_eliminar_').Update(disabled=True)
            lista_titulaciones = filtra_titulaciones(tabla_titulaciones)
            window.Element('_titulacion_').Update(
                values=['---'] + lista_titulaciones,
                disabled=False
            )
            window.Element('_cancelar_').Update(disabled=False)
        # ---
        elif event == '_eliminar_':
            uuid_bita = values['_docencia_asignada_'][-36:]
            tmp_series = bitacora.loc[uuid_bita].copy()
            if tmp_series.ndim != 1:
                print(tmp_series)
                raise ValueError('Something is wrong with tmpdf')
            uuid_prof = tmp_series['uuid_prof']
            uuid_titu = tmp_series['uuid_titu']
            uuid_asig = tmp_series['uuid_asig']
            creditos_a_recuperar = tmp_series['creditos_elegidos']
            dummy = sg.PopupYesNo('Do you really want to remove this subject?')
            if dummy == 'Yes':
                devolucion_correcta = True
                if tabla_profesores.loc[
                    uuid_prof, 'asignados'
                ] >= creditos_a_recuperar:
                    tabla_profesores.loc[
                        uuid_prof, 'asignados'
                    ] -= creditos_a_recuperar
                    tabla_profesores.loc[
                        uuid_prof, 'diferencia'
                    ] = tabla_profesores.loc[uuid_prof, 'asignados'] - \
                        tabla_profesores.loc[uuid_prof, 'encargo']
                else:
                    print('¡El profesor no tiene créditos suficientes!')
                    input('Press <CR> to continue...')
                    devolucion_correcta = False
                if devolucion_correcta:
                    titulacion = tabla_titulaciones.loc[uuid_titu][
                        'titulacion']
                    tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
                    tabla_asignaturas.loc[
                        uuid_asig, 'creditos_disponibles'
                    ] += creditos_a_recuperar
                    tabla_titulaciones.loc[
                        uuid_titu, 'creditos_disponibles'
                    ] = tabla_asignaturas['creditos_disponibles'].sum()
                    sumproduct = tabla_asignaturas['creditos_disponibles'] * \
                                 tabla_asignaturas['bec_col']
                    tabla_titulaciones.loc[
                        uuid_titu, 'creditos_elegidos'
                    ] = tabla_titulaciones.loc[uuid_titu,
                                               'creditos_iniciales'] - \
                          tabla_titulaciones.loc[uuid_titu,
                                                 'creditos_disponibles']
                    tabla_titulaciones.loc[uuid_titu, 'creditos_beccol'] = \
                        sumproduct.sum()
                    # set date_removed
                    bitacora.loc[uuid_bita, 'date_removed'] = \
                        str(datetime.now())
                # update info for teacher
                encargo = tabla_profesores.loc[uuid_prof]['encargo']
                asignados = tabla_profesores.loc[uuid_prof]['asignados']
                diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(round(diferencia, 4))
                seleccion_del_profesor = filtra_seleccion_del_profesor(
                    uuid_prof, bitacora
                )
                if len(seleccion_del_profesor) > 1:
                    window.Element('_docencia_asignada_').Update(
                        values=seleccion_del_profesor,
                        disabled=False
                    )
                else:
                    window.Element('_docencia_asignada_').Update(
                        values=['---'],
                        disabled=True
                    )
                window.Element('_eliminar_').Update(disabled=True)
                update_info_creditos()
                export_to_html_bitacora(bitacora)
                export_to_html_titulaciones(tabla_titulaciones)
                export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas)
                export_to_html_profesores(tabla_profesores, bitacora)
        # ---
        elif event == '_titulacion_':
            titulacion = values['_titulacion_']
            if titulacion == '---':
                window.Element('_asignatura_elegida_').Update('---')
                window.Element('_asignatura_elegida_').Update(disabled=True)
                window.Element('_fraccion_todo_').Update(
                    value=False, disabled=True
                )
                window.Element('_fraccion_parte_').Update(
                    value=False, disabled=True
                )
                window.Element('_creditos_elegidos_').Update(
                    str(0.0)
                )
                window.Element('_explicacion_').Update(
                    value=' ', disabled=True
                )
                window.Element('_aplicar_').Update(disabled=True)
            else:
                uuid_titu = values['_titulacion_'][-36:]
                titulacion = tabla_titulaciones.loc[uuid_titu][
                    'titulacion']
                tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
                lista_asignaturas = filtra_asignaturas(
                    tabla_asignaturas,
                    values['_excluir_asignaturas_beccol_']
                )
                window.Element('_asignatura_elegida_').Update(
                    values=['---'] + lista_asignaturas,
                    disabled=False
                )
                window.Element('_fraccion_todo_').Update(
                    value=False, disabled=True
                )
                window.Element('_fraccion_parte_').Update(
                    value=False, disabled=True
                )
                window.Element('_creditos_elegidos_').Update(
                    str(0.0)
                )
                window.Element('_explicacion_').Update(
                    value=' ', disabled=True
                )
        # ---
        elif event == '_asignatura_elegida_':
            asignatura_elegida = values['_asignatura_elegida_']
            if asignatura_elegida == '---':
                window.Element('_fraccion_todo_').Update(
                    value=False, disabled=True
                )
                window.Element('_fraccion_parte_').Update(
                    value=False, disabled=True
                )
                window.Element('_creditos_elegidos_').Update(
                    str(0.0)
                )
                window.Element('_explicacion_').Update(
                    value=' ', disabled=True
                )
                window.Element('_aplicar_').Update(disabled=True)
            else:
                uuid_titu = values['_titulacion_'][-36:]
                uuid_asig = values['_asignatura_elegida_'][-36:]
                titulacion = tabla_titulaciones.loc[uuid_titu][
                    'titulacion']
                creditos_max_asignatura = bigdict_tablas_asignaturas[
                    titulacion].loc[uuid_asig]['creditos_disponibles']
                window.Element('_fraccion_todo_').Update(
                    value=False, disabled=False
                )
                window.Element('_fraccion_parte_').Update(
                    value=False, disabled=False
                )
                window.Element('_creditos_elegidos_').Update(
                    str(round(
                        bigdict_tablas_asignaturas[titulacion].loc[
                            uuid_asig]['creditos_disponibles'],4)
                    )
                )
                window.Element('_aplicar_').Update(disabled=True)
        # ---
        elif event == '_fraccion_todo_':
            window.Element('_fraccion_todo_').Update(
                value=True
            )
            window.Element('_fraccion_parte_').Update(
                value=False
            )
            window.Element('_label_creditos_elegidos_').Update(
                text_color="#aaaaaa"
            )
            window.Element('_creditos_elegidos_').Update(
                value=str(round(creditos_max_asignatura, 4)),
                disabled=True,
            )
            window.Element('_explicacion_').Update(
                value=' ', disabled=False
            )
            window.Element('_aplicar_').Update(disabled=False)
        # ---
        elif event == '_fraccion_parte_':
            window.Element('_fraccion_todo_').Update(
                value=False
            )
            window.Element('_fraccion_parte_').Update(
                value=True
            )
            loop = True
            creditos_elegidos = \
                values['_creditos_elegidos_']
            limite_maximo = creditos_max_asignatura
            while loop:
                dumtxt = sg.PopupGetText(
                    '¿Créditos a elegir?  (0 < valor < ' +
                    str(limite_maximo) + ')',
                    '¿Créditos?'
                )
                if dumtxt is None:
                    loop = False
                else:
                    lfloat = True
                    try:
                        creditos_elegidos = float(dumtxt)
                    except ValueError:
                        sg.Popup('ERROR', 'Número inválido')
                        lfloat = False
                    if lfloat:
                        if 0 < creditos_elegidos < limite_maximo:
                            loop = False
                        else:
                            sg.Popup('ERROR',
                                     '¡Número fuera del intervalo válido!\n' +
                                     '0 < valor < ' + str(limite_maximo))
            window.Element('_creditos_elegidos_').Update(
                           str(float(creditos_elegidos))
            )
            window.Element('_explicacion_').Update(
                value=' ', disabled=False
            )
            window.Element('_aplicar_').Update(disabled=False)
        # ---
        elif event == '_aplicar_':
            uuid_prof = values['_profesor_'][-36:]
            uuid_titu = values['_titulacion_'][-36:]
            uuid_asig = values['_asignatura_elegida_'][-36:]
            creditos_elegidos = float(values['_creditos_elegidos_'])
            titulacion = tabla_titulaciones.loc[uuid_titu]['titulacion']
            tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
            # evitamos restar dos números reales iguales para evitar errores
            # de redondeo
            # ojo: ver sintaxis para evitar problemas de modificación de
            # una columna ('creditos_disponibles') que se ha generado como
            # una copia de otra ('creditos_iniciales')
            asignacion_es_correcta = True
            if values['_fraccion_todo_']:
                tabla_asignaturas.loc[uuid_asig,
                                      'creditos_disponibles'] = 0
            elif values['_fraccion_parte_']:
                if tabla_asignaturas.loc[
                    uuid_asig, 'creditos_disponibles'
                ] > creditos_elegidos:
                    tabla_asignaturas.loc[
                        uuid_asig, 'creditos_disponibles'
                    ] -= creditos_elegidos
                else:
                    print('¡Créditos disponibles insuficientes!')
                    input('Press <CR> to continue...')
                    asignacion_es_correcta = False
            else:
                print('¡Fracción de asignatura no establecida!')
                input('Press <CR> to continue...')
                asignacion_es_correcta = False
            if asignacion_es_correcta:
                tabla_titulaciones.loc[
                    uuid_titu, 'creditos_disponibles'
                ] = tabla_asignaturas['creditos_disponibles'].sum()
                sumproduct = tabla_asignaturas['creditos_disponibles'] * \
                             tabla_asignaturas['bec_col']
                tabla_titulaciones.loc[
                    uuid_titu, 'creditos_elegidos'
                ] = tabla_titulaciones.loc[
                                        uuid_titu, 'creditos_iniciales'
                                    ] - \
                      tabla_titulaciones.loc[
                          uuid_titu, 'creditos_disponibles'
                      ]
                tabla_titulaciones.loc[uuid_titu, 'creditos_beccol'] = \
                    sumproduct.sum()
                tabla_profesores.loc[
                    uuid_prof, 'asignados'
                ] += creditos_elegidos
                tabla_profesores.loc[
                    uuid_prof, 'diferencia'
                ] = tabla_profesores.loc[uuid_prof, 'asignados'] - \
                    tabla_profesores.loc[uuid_prof, 'encargo']
                update_info_creditos()
                encargo = tabla_profesores.loc[uuid_prof]['encargo']
                asignados = tabla_profesores.loc[uuid_prof]['asignados']
                diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(round(diferencia, 4))
            # Nota: uuid_bita tendrá un valor único para cada elección de los
            # profesores. Esto permite discriminar dentro de una misma
            # asignatura (i.e., mismo uuid_prof, uuid_titu,
            # uuid_asig) cuando se eligen fracciones de asignatura (es
            # decir, cuando se subdividen asignaturas por un mismo profesor)
            uuid_bita = str(new_uuid(megalist_uuid))
            megalist_uuid += [uuid_bita]
            # prepare new entry for bitacora
            data_row = [uuid_prof, uuid_titu, uuid_asig,
                        str(datetime.now()), 'None',
                        creditos_elegidos, values['_explicacion_']]
            for item in csv_colnames_profesor:
                data_row.append(tabla_profesores.loc[uuid_prof][item])
            for item in csv_colnames_asignatura:
                data_row.append(tabla_asignaturas.loc[uuid_asig][item])
            new_entry = pd.DataFrame(data=[data_row],
                                     index=[uuid_bita],
                                     columns=bitacora.columns.tolist())
            bitacora = pd.concat([bitacora, new_entry])
            bitacora.index.name = 'uuid_bita'
            if args.debug:
                print(bitacora)
            clear_screen_asignatura()
            window.Element('_profesor_').Update(disabled=False)
            seleccion_del_profesor = filtra_seleccion_del_profesor(
                uuid_prof, bitacora
            )
            if len(seleccion_del_profesor) > 1:
                window.Element('_docencia_asignada_').Update(
                    values=seleccion_del_profesor,
                    disabled=False
                )
            else:
                window.Element('_docencia_asignada_').Update(
                    values=['---'],
                    disabled=True
                )
            window.Element('_continuar_').Update(disabled=False)
            export_to_html_bitacora(bitacora)
            export_to_html_titulaciones(tabla_titulaciones)
            export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas)
            export_to_html_profesores(tabla_profesores, bitacora)
        # ---
        elif event == '_cancelar_':
            clear_screen_asignatura()
            window.Element('_profesor_').Update(disabled=False)
            uuid_prof = values['_profesor_'][-36:]
            seleccion_del_profesor = filtra_seleccion_del_profesor(
                uuid_prof, bitacora
            )
            if len(seleccion_del_profesor) > 1:
                window.Element('_docencia_asignada_').Update(
                    values=seleccion_del_profesor,
                    disabled=False
                )
            else:
                window.Element('_docencia_asignada_').Update(
                    values=['---'],
                    disabled=True
                )
            window.Element('_continuar_').Update(disabled=False)
        # ---
        elif event is None or event == "_salir_":
            coption = ''
            while coption != 'y' and coption != 'n':
                coption = input('Do you really want to exit (y/n) [y] ? ')
                if coption == '':
                    coption = 'y'
                if coption != 'y' and coption != 'n':
                    print('Invalid answer. Try again!')
            if coption == 'y':
                break

    window.Close()


if __name__ == "__main__":

    main()
