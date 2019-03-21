import argparse
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import sys


WIDTH_HLINE = 90
WIDTH_TEXT_SUMMARY = 25
WIDTH_TEXT_LABEL = 18
WIDTH_TEXT_UUID = 30
WIDTH_INPUT_COMBO = 50
WIDTH_INPUT_NUMBER = 10
WIDTH_SPACES_FOR_UUID = 150


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
        names = ['uuid', 'titulacion']
        converters = {'uuid': str, 'titulacion': str}
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
    lok = tabla_inicial['uuid'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_titulaciones = tabla_inicial.copy()
    tabla_titulaciones.index = tabla_inicial['uuid']
    del tabla_titulaciones['uuid']

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
        usecols = range(1, 12)
        names = ['curso', 'semestre', 'codigo', 'asignatura', 'area',
                 'uuid', 'creditos_iniciales', 'comentarios', 'grupo',
                 'bec_col', 'profesor_anterior'
                 ]
        converters = {'curso': str, 'semestre': int, 'codigo': int,
                      'area': str, 'uuid': str, 'creditos_iniciales': float,
                      'comentarios': str_nonan, 'grupo': str_nonan,
                      'bec_col': int, 'profesor_anterior': str_nonan
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
    lok = tabla_inicial['uuid'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # fill empty cells
    for item in ['curso', 'semestre', 'codigo', 'asignatura']:
        tabla_inicial[item] = \
            fill_cell_with_previous_value(tabla_inicial[item])

    # use uuid as index
    tabla_asignaturas = tabla_inicial.copy()
    tabla_asignaturas.index = tabla_inicial['uuid']
    del tabla_asignaturas['uuid']

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
        names = ['uuid', 'apellidos', 'nombre', 'categoria', 'encargo']
        converters = {'uuid': str,
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
    lok = tabla_inicial['uuid'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_profesores = tabla_inicial.copy()
    tabla_profesores.index = tabla_inicial['uuid']
    del tabla_profesores['uuid']

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
            if values[key][-41:-36] == 'uuid=':
                output += "'" + values[key][:-41].rstrip() + " ... " + \
                          values[key][-41:] + "'"
            else:
                output += "'" + values[key] + "'"
        else:
            output += str(values[key])
        print(output)


def define_layout(fontsize):
    """Define GUI layout

    """

    # define monospaced typeface for results
    fontname = 'courier ' + str(fontsize)

    layout = [[sg.Text('Encargo docente total (créditos):',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='right'),
               sg.Text('0.0', font=fontname,
                       key='_summary_total_')],
              [sg.Text('Disponible:',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='right'),
               sg.Text('0.0', font=fontname,
                       key='_summary_disponible_')],
              [sg.Text('Disponible para Bec./Col.:',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='right'),
               sg.Text('0.0', font=fontname,
                       key='_summary_disponible_beccol_')],
              # ---
              [sg.Checkbox('Excluir asignaturas para becarios/colaboradores',
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
                           key='_excluir_RyC_')],
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
              [sg.Button('Aplicar', disabled=True, key='_aplicar_'),
               sg.Button('Cancelar', disabled=True, key='_cancelar_')],
              [sg.Text('_' * WIDTH_HLINE)],
              [sg.Button('Salir', key='_salir_')]
              ]

    return layout


def main(args=None):

    # parse command-line options
    parser = argparse.ArgumentParser(description='Subject assignment tool')

    parser.add_argument("xlsxfile",
                        help="Excel file with input data",
                        type=argparse.FileType('rt'))
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

    # variable para almacenar los UUIDs de titulaciones, asignaturas
    # y profesores
    dumdumlist = []

    # titulaciones
    tabla_titulaciones = read_tabla_titulaciones(
        xlsxfilename=args.xlsxfile.name,
        course=args.course,
        debug=args.debug
    )
    dumdumlist += tabla_titulaciones.index.tolist()

    # asignaturas de cada titulacion
    bigdict_tablas_asignaturas = {}
    for titulacion in tabla_titulaciones['titulacion']:
        dumtable = read_tabla_asignaturas(
                xlsxfilename=args.xlsxfile.name,
                course=args.course,
                sheet_name=titulacion,
                debug=args.debug
            )
        # incluye columna con créditos disponibles
        dumtable['creditos_disponibles'] = dumtable['creditos_iniciales']
        bigdict_tablas_asignaturas[titulacion] = dumtable.copy()
    # comprueba que los UUIDs son únicos al mezclar todas las asignaturas
    dumlist = []
    for titulacion in tabla_titulaciones['titulacion']:
        dumtable = bigdict_tablas_asignaturas[titulacion]
        dumlist += dumtable.index.tolist()
    if len(dumlist) != len(set(dumlist)):
        for uuid in dumlist:
            if dumlist.count(uuid) > 1:
                print(uuid)
        raise ValueError('UUIDs are not unique when mixing all the subjects!')
    dumdumlist += dumlist

    # profesores
    tabla_profesores = read_tabla_profesores(
        xlsxfilename=args.xlsxfile.name,
        course=args.course,
        debug=args.debug
    )
    dumdumlist += tabla_profesores.index.tolist()
    # transforma el encargo de cada profesor de horas a créditos
    tabla_profesores['encargo'] /= 10
    # define columna para almacenar docencia elegida
    tabla_profesores['asignados'] = 0.0

    # comprueba que los UUIDs de titulaciones, asignaturas y profesores
    # son todos distintos
    if len(dumdumlist) != len(set(dumdumlist)):
        for uuid in dumdumlist:
            if dumdumlist.count(uuid) > 1:
                print(uuid)
        raise ValueError('UUIDs are not unique when mixing everything!')

    # ---

    # set global GUI options
    sg.SetOptions(font=(args.fontname, args.fontsize))

    # define GUI layout
    layout = define_layout(args.fontsize)
    #sg.Text(str(tabla_profesores['encargo'].sum()),

    # define GUI window
    window = sg.Window('Reparto Docente (FTA), Curso ' +
                       args.course).Layout(layout)

    # ---

    creditos_max_asignatura = 0.0

    def clear_screen_profesor(profesor_disabled=True):
        if profesor_disabled:
            window.Element('_profesor_').Update(values='---', disabled=True)
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
        window.Element('_aplicar_').Update(disabled=True)
        window.Element('_cancelar_').Update(disabled=True)

    while True:
        event, values = window.Read()
        display_in_terminal(event, values)
        if event == '_excluir_asignaturas_beccol_':
            clear_screen_profesor()
            clear_screen_asignatura()
        elif event == '_excluir_RyC_':
            clear_screen_asignatura()
            clear_screen_profesor()
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
                        if not 'RyC' in tabla_profesores['categoria'][i] or \
                            not values['_excluir_RyC_']:
                            nombre_completo = tabla_profesores['nombre'][i] +\
                                              ' ' +\
                                              tabla_profesores['apellidos'][i]
                            ldum = len(nombre_completo)
                            if ldum < WIDTH_SPACES_FOR_UUID:
                                nombre_completo += \
                                    (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                            nombre_completo += ' uuid=' + tabla_profesores.index[i]
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
        elif event == '_profesor_':
            if values['_profesor_'] == '---':
                clear_screen_profesor(profesor_disabled=False)
            else:
                uuid_profesor = values['_profesor_'][-36:]
                encargo = tabla_profesores.loc[uuid_profesor]['encargo']
                asignados = tabla_profesores.loc[uuid_profesor]['asignados']
                diferencia = asignados - encargo
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(round(diferencia, 4))
                window.Element('_continuar_').Update(disabled=False)
        elif event == '_continuar_':
            uuid_profesor = values['_profesor_'][-36:]
            if uuid_profesor is None:
                raise ValueError('Unexpected uuid_profesor == None')
            window.Element('_profesor_').Update(disabled=True)
            window.Element('_continuar_').Update(disabled=True)
            lista_titulaciones = ['---']
            num_titulaciones = tabla_titulaciones.shape[0]
            for i in range(num_titulaciones):
                nombre_titulacion = tabla_titulaciones['titulacion'][i]
                ldum = len(nombre_titulacion)
                if ldum < WIDTH_SPACES_FOR_UUID:
                    nombre_titulacion += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                nombre_titulacion += ' uuid=' + tabla_titulaciones.index[i]
                lista_titulaciones.append(nombre_titulacion)
            window.Element('_titulacion_').Update(
                values=lista_titulaciones, disabled=False)
            window.Element('_cancelar_').Update(disabled=False)
        elif event == '_titulacion_':
            titulacion = values['_titulacion_']
            if titulacion == '---':
                uuid_titulacion = None
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
                window.Element('_aplicar_').Update(disabled=True)
            else:
                uuid_titulacion = values['_titulacion_'][-36:]
                titulacion = tabla_titulaciones.loc[uuid_titulacion][
                    'titulacion']
                tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
                num_asignaturas = tabla_asignaturas.shape[0]
                lista_asignaturas = []
                for i in range(num_asignaturas):
                    dumtxt = \
                        tabla_asignaturas['asignatura'][i] + ', ' + \
                        str(round(
                            tabla_asignaturas['creditos_disponibles'][i], 4
                        )) + ' créditos'
                    if tabla_asignaturas['comentarios'][i] != ' ':
                        dumtxt += ', ' + tabla_asignaturas['comentarios'][i]
                    if tabla_asignaturas['grupo'][i] != ' ':
                        dumtxt += ', grupo ' + tabla_asignaturas['grupo'][i]
                    ldum = len(dumtxt)
                    if ldum < WIDTH_SPACES_FOR_UUID:
                        dumtxt += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                    dumtxt += ' uuid=' + tabla_asignaturas.index[i]
                    lista_asignaturas.append(dumtxt)
                window.Element('_asignatura_elegida_').Update(
                    values=['---'] + lista_asignaturas,
                    disabled=False
                )
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
                window.Element('_aplicar_').Update(disabled=True)
            else:
                uuid_titulacion = values['_titulacion_'][-36:]
                uuid_asignatura = values['_asignatura_elegida_'][-36:]
                titulacion = tabla_titulaciones.loc[uuid_titulacion][
                    'titulacion']
                creditos_max_asignatura = bigdict_tablas_asignaturas[
                    titulacion].loc[uuid_asignatura]['creditos_disponibles']
                window.Element('_fraccion_todo_').Update(
                    disabled=False
                )
                window.Element('_fraccion_parte_').Update(
                    disabled=False
                )
                window.Element('_creditos_elegidos_').Update(
                    str(round(
                        bigdict_tablas_asignaturas[titulacion].loc[
                            uuid_asignatura]['creditos_disponibles'],4)
                    )
                )
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
            window.Element('_aplicar_').Update(disabled=False)
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
            window.Element('_aplicar_').Update(disabled=False)
        elif event == '_aplicar_':
            uuid_profesor = values['_profesor_'][-36:]
            uuid_titulacion = values['_titulacion_'][-36:]
            uuid_asignatura = values['_asignatura_elegida_'][-36:]
            print('* uuid_profesor....: ' + uuid_profesor)
            print('* uuid_titulacion..: ' + uuid_titulacion)
            print('* uuid_asignatura..: ' + uuid_asignatura)
            creditos_elegidos = float(
                values['_creditos_elegidos_']
            )
            print('* creditos elegidos: ' +
                  values['_creditos_elegidos_'])
            #
            titulacion = tabla_titulaciones.loc[uuid_titulacion]['titulacion']
            print('>> titulación: ' + titulacion)
            tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
            print('-> créditos iniciales..: ',
                  tabla_asignaturas.loc[uuid_asignatura]['creditos_iniciales'])
            print('-> créditos disponibles: ',
                  tabla_asignaturas.loc[uuid_asignatura]['creditos_disponibles'])
            print('-> aplicamos eleccion...')
            # evitamos restar dos números reales iguales para evitar errores
            # de redondeo
            # ojo: ver sintaxis para evitar problemas de modificación de
            # una columna ('creditos_disponibles') que se ha generado como
            # una copia de otra ('creditos_iniciales')
            if values['_fraccion_todo_']:
                tabla_asignaturas.loc[uuid_asignatura,
                                      'creditos_disponibles'] = 0
            elif values['_fraccion_parte_']:
                if tabla_asignaturas.loc[uuid_asignatura,
                                         'creditos_disponibles'] > \
                        creditos_elegidos:
                    tabla_asignaturas.loc[uuid_asignatura,
                                          'creditos_disponibles'] -= \
                        creditos_elegidos
                else:
                    raise ValueError('Créditos disponibles insuficiente')
            else:
                raise ValueError('Fracción de asignatura no establecida')
            print('-> créditos iniciales..: ',
                  tabla_asignaturas.loc[uuid_asignatura]['creditos_iniciales'])
            print('-> créditos disponibles: ',
                  tabla_asignaturas.loc[uuid_asignatura]['creditos_disponibles'])
        elif event == '_cancelar_':
            window.Element('_profesor_').Update(disabled=False)
            window.Element('_continuar_').Update(disabled=False)
            window.Element('_titulacion_').Update(
                values='---',
                disabled=True
            )
            window.Element('_asignatura_elegida_').Update(
                values='---',
                disabled=True
            )
            window.Element('_fraccion_todo_').Update(
                value=False, disabled=True
            )
            window.Element('_fraccion_parte_').Update(
                value=False, disabled=True
            )
            window.Element('_creditos_elegidos_').Update(
                value='0.0', disabled=True
            )
            window.Element('_aplicar_').Update(disabled=True)
            window.Element('_cancelar_').Update(disabled=True)
        elif event is None or event == "_salir_":
            cout = ''
            while cout != 'y' and cout != 'n':
                cout = input('Do you really want to exit (y/n) [y] ? ')
                if cout == '':
                    cout = 'y'
                if cout != 'y' and cout != 'n':
                    print('Invalid answer. Try again!')
            if cout == 'y':
                break

    window.Close()


if __name__ == "__main__":

    main()
