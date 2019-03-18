import argparse
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import sys


WIDTH_HLINE = 90
WIDTH_TEXT_LABEL = 18
WIDTH_INPUT_COMBO = 50
WIDTH_INPUT_NUMBER = 10


def fill_cell_with_previous_value(s):
    """Return list removing NaN in Series

    """

    l = len(s)
    result = []
    i = 0
    last = None
    while i < l:
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


def read_tabla_titulaciones(xlsxfilename, debug=False):
    """Lee hoja Excel con lista de titulaciones.

    """

    if debug:
        print('Reading ' + xlsxfilename)
        print('-> Sheet: "Resumen Encargo"')

    tabla_titulaciones = pd.read_excel(
        xlsxfilename,
        sheet_name='Resumen Encargo',
        skiprows=4,
        header=None,
        usecols=[1,2],
        names=['uuid', 'titulacion'],
        converters={'uuid': str,
                    'titulacion': str}
    )

    # remove unnecessary rows
    lok = tabla_titulaciones['uuid'].notnull()
    tabla_titulaciones = tabla_titulaciones[lok]

    # reset index values
    tabla_titulaciones = tabla_titulaciones.reset_index(drop=True)

    if debug:
        print(tabla_titulaciones)
        input('Press <CR> to continue...')

    return tabla_titulaciones


def read_tabla_asignaturas(xlsxfilename, sheetname, skiprows=None,
                           usecols=None, debug=False):
    """Lee hoja Excel con lista de asignaturas

    """

    if debug:
        print('Reading ' + xlsxfilename)
        print('-> Sheet: "' + sheetname + '"')

    tabla_asignaturas = pd.read_excel(
        xlsxfilename,
        sheet_name=sheetname,
        skiprows=skiprows,
        header=None,
        usecols=usecols,
        names=['curso', 'semestre', 'codigo', 'asignatura', 'area', 'uuid',
               'creditos', 'comentarios', 'grupo', 'profesor_anterior'],
        converters={'curso': str, 'semestre': int, 'codigo': int, 'area': str,
                    'uuid': str, 'creditos': float, 'comentarios': str,
                    'grupo': str, 'profesor_anterior': str}
    )

    # remove unnecessary rows
    lok = tabla_asignaturas['uuid'].notnull()
    tabla_asignaturas = tabla_asignaturas[lok]

    # reset index values
    tabla_asignaturas = tabla_asignaturas.reset_index(drop=True)

    # fill empty cells
    for item in ['curso', 'semestre', 'codigo', 'asignatura']:
        tabla_asignaturas[item] = \
            fill_cell_with_previous_value(tabla_asignaturas[item])

    if(debug):
        print(tabla_asignaturas)
        print('Créditos totales:', tabla_asignaturas['creditos'].sum())
        input("Stop here!")

    return tabla_asignaturas


def read_tabla_profesores(xlsxfilename, debug=False):
    """Lee hoja Excel con lista de profesores que participan en rondas

    """

    if debug:
        print('Reading ' + xlsxfilename)
        print('-> Sheet: "PDA"')

    tabla_profesores = pd.read_excel(
        xlsxfilename,
        sheet_name='PDA',
        skiprows=2,
        header=None,
        usecols=[0, 1, 2, 3, 17],
        names=['uuid', 'apellidos', 'nombre', 'categoria', 'encargo'],
        converters={'uuid': str,
                    'apellidos': str,
                    'nombre': str,
                    'categoria': str,
                    'encargo': float}
    )

    # remove unnecessary rows
    lok = tabla_profesores['uuid'].notnull()
    tabla_profesores = tabla_profesores[lok]

    # reset index values
    tabla_profesores = tabla_profesores.reset_index(drop=True)

    if debug:
        print(tabla_profesores)
        print('Encargo total:', tabla_profesores['encargo'].sum())
        input('Stop here!')

    return tabla_profesores


def busca_profesor(profesor, tabla_profesores):
    """Return index of 'profesor' within tabla_profesores.

    """

    nombre_completo = None
    for i, (nombre, apellidos) in enumerate(zip(tabla_profesores['nombre'],
                                                tabla_profesores['apellidos'])
                                            ):
        nombre_completo = nombre + ' ' + apellidos
        if nombre_completo == profesor:
            return i

    raise ValueError('¡Profesor ' + nombre_completo + ' no encontrado!')


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

    tabla_titulaciones = read_tabla_titulaciones(
        xlsxfilename=args.xlsxfile.name,
        debug=args.debug
    )
    lista_titulaciones = ['---'] + tabla_titulaciones['titulacion'].tolist()
    print(lista_titulaciones)

    if args.course == '2019-2020':
        skiprows=5
        usecols=range(1,11)
    else:
        raise ValueError("Unexpected course!")
    lista_tablas_asignaturas = []
    for titulacion in tabla_titulaciones['titulacion']:
        lista_tablas_asignaturas.append(
            read_tabla_asignaturas(
                xlsxfilename=args.xlsxfile.name,
                sheetname=titulacion,
                skiprows=skiprows,
                usecols=usecols,
                debug=args.debug
            )
        )

    tabla_profesores = read_tabla_profesores(
        xlsxfilename=args.xlsxfile.name,
        debug=args.debug
    )

    num_profesores = tabla_profesores.shape[0]

    lista_profesores = ['---'] + \
                       [tabla_profesores['nombre'][i] + ' ' +
                        tabla_profesores['apellidos'][i]
                        for i in range(num_profesores)]

    sg.SetOptions(font=(args.fontname, args.fontsize))

    layout = [[sg.T('Resumen...')],
              [sg.T('_' * WIDTH_HLINE)],
              # ---
              [sg.T('Profesor/a:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_profesor_'),
               sg.InputCombo(values=lista_profesores,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_profesor_')],
              # ---
              [sg.T('Encargo docente:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_encargo_docente_'),
               sg.T('---', key='_encargo_docente_',
                    size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.T('Créditos asignados:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_creditos_asignados_'),
               sg.T('---', key='_creditos_asignados_',
                    size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.T('Diferencia:', size=(
                  WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_diferencia_creditos_'),
               sg.T('---', key='_diferencia_creditos_',
                    size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.T('Docencia asignada:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_docencia_asignada_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_docencia_asignada_')],
              # ---
              [sg.Button('Continuar', disabled=True),
               sg.Button('Modificar', disabled=True)],
              [sg.T('_' * WIDTH_HLINE)],
              # ---
              [sg.T('Titulación:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_titulacion_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_titulacion_')],
              # ---
              [sg.T('Asignatura elegida:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_asignatura_elegida_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_asignatura_elegida_'),
               sg.T('Créditos: ' + str(0.0),
                    key='_creditos_asignatura_elegida_')],
              [sg.T('', size=(WIDTH_TEXT_LABEL,1)),
               sg.Radio('Todos los créditos',
                        '_fraccion_de_asignatura_',
                        default=True, size=(WIDTH_TEXT_LABEL,1),
                        disabled=True),
               sg.Radio('Solo una parte', '_fraccion_asignatura_',
                        default=False, size=(WIDTH_TEXT_LABEL,1),
                        disabled=True),
               sg.T('Créditos elegidos'),
               sg.InputText(default_text='0.0', size=(WIDTH_INPUT_NUMBER,1),
                            justification='right',
                            do_not_clear=True, disabled=True,
                            key='_creditos_elegidos_de_asignatura_')],
              # ---
              [sg.Button('Aplicar', disabled=True),
               sg.Button('Cancelar', disabled=True)],
              [sg.T('_' * WIDTH_HLINE)],
              [sg.Button('Salir')]
              ]

    window = sg.Window("Reparto Docente (FTA)").Layout(layout)

    while True:
        event, values = window.Read()
        print(event, values)
        if event is None or event == "Salir":
            cout = ''
            while cout != 'y' and cout != 'n':
                cout = input('Do you really want to exit (y/n) [y] ? ')
                if cout == '':
                    cout = 'y'
                if cout != 'y' and cout != 'n':
                    print('Invalid answer. Try again!')
            if cout == 'y':
                break
        elif event == "Cancelar":
            window.Element('_profesor_').Update(values=lista_profesores)
            window.Element('_titulacion_').Update(values='---', disabled=True)
            window.Element('_asignatura_').Update(values='---', disabled=True)
        elif event == "Aplicar":
            break
        elif event == '_profesor_':
            if values['_profesor_'] == '---':
                window.Element('_encargo_docente_').Update('---')
                window.Element('_creditos_asignados_').Update('---')
                window.Element('_diferencia_creditos_').Update('---')
                window.Element('_docencia_asignada_').Update('---')
                window.Element('_titulacion_').Update('---')
            else:
                iprof = busca_profesor(values['_profesor_'], tabla_profesores)
                window.Element('_encargo_docente_').Update(
                    str(round(tabla_profesores['encargo'][iprof], 4)))
                window.Element('_titulacion_').Update(
                    values=lista_titulaciones, disabled=False)
        elif event == '_titulacion_':
            if values['_titulacion_'] == '---':
                window.Element('_asignatura_elegida_').Update('---')
                window.Element('_asignatura_elegida_').Update(disabled=True)
            else:
                window.Element('_asignatura_elegida_').Update(disabled=False)
            print(values['_titulacion_'])
            input("Stop here!")
            '''
            if values['_titulacion_'] == 'Grado en Física':
                window.Element('_asignatura_').Update(
                    values=list_asignaturas_grado_fisica)
            elif values['_titulacion_'] == 'Grado en IEC':
                window.Element('_asignatura_').Update(
                    values=list_asignaturas_grado_iec)
            elif values['_titulacion_'] == 'Otros grados':
                window.Element('_asignatura_').Update(
                    values=list_asignaturas_otros_grados)
            elif values['_titulacion_'] == 'Másteres':
                window.Element('_asignatura_').Update(
                    values=list_asignaturas_masteres)
            '''

    window.Close()


if __name__ == "__main__":

    main()
