import argparse
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import sys


WIDTH_HLINE = 90
WIDTH_TEXT_LABEL = 18
WIDTH_INPUT_COMBO = 50
WIDTH_INPUT_NUMBER = 10


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

    tabla_inicial = pd.read_excel(
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
    lok = tabla_inicial['uuid'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_titulaciones = tabla_inicial.copy()
    tabla_titulaciones.index = tabla_inicial['uuid']
    del tabla_titulaciones['uuid']

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

    tabla_inicial = pd.read_excel(
        xlsxfilename,
        sheet_name=sheetname,
        skiprows=skiprows,
        header=None,
        usecols=usecols,
        names=['curso', 'semestre', 'codigo', 'asignatura', 'area', 'uuid',
               'creditos', 'comentarios', 'grupo', 'profesor_anterior'],
        converters={'curso': str, 'semestre': int, 'codigo': int, 'area': str,
                    'uuid': str, 'creditos': float,
                    'comentarios': str_nonan,
                    'grupo': str_nonan,
                    'profesor_anterior': str_nonan}
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

    tabla_inicial = pd.read_excel(
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
    lok = tabla_inicial['uuid'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_profesores = tabla_inicial.copy()
    tabla_profesores.index = tabla_inicial['uuid']
    del tabla_profesores['uuid']

    if debug:
        print(tabla_profesores)
        print('Encargo total:', tabla_profesores['encargo'].sum())
        input('Stop here!')

    return tabla_profesores


def busca_profesor_por_nombre_completo(profesor, tabla_profesores):
    """Return index of 'profesor' within tabla_profesores.

    """

    nombre_completo = None
    for i, (nombre, apellidos) in enumerate(zip(
            tabla_profesores['nombre'],
            tabla_profesores['apellidos'])):
        nombre_completo = nombre + ' ' + apellidos
        if nombre_completo == profesor:
            return tabla_profesores.index[i]

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

    # titulaciones
    tabla_titulaciones = read_tabla_titulaciones(
        xlsxfilename=args.xlsxfile.name,
        debug=args.debug
    )
    lista_titulaciones = ['---'] + tabla_titulaciones['titulacion'].tolist()

    # asignaturas de cada titulacion
    if args.course == '2019-2020':
        skiprows=5
        usecols=range(1,11)
    else:
        raise ValueError("Unexpected course!")
    dict_tablas_asignaturas = {}
    for titulacion in tabla_titulaciones['titulacion']:
        dict_tablas_asignaturas[titulacion] = read_tabla_asignaturas(
                xlsxfilename=args.xlsxfile.name,
                sheetname=titulacion,
                skiprows=skiprows,
                usecols=usecols,
                debug=args.debug
            )

    # profesores
    tabla_profesores = read_tabla_profesores(
        xlsxfilename=args.xlsxfile.name,
        debug=args.debug
    )
    tabla_profesores['asignados'] = 0.0

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
                    key='_label_encargo_'),
               sg.T('---', key='_encargo_',
                    size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.T('Créditos asignados:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_asignados_'),
               sg.T('---', key='_asignados_',
                    size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.T('Diferencia:', size=(
                  WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_diferencia_'),
               sg.T('---', key='_diferencia_',
                    size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.T('Docencia asignada:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_docencia_asignada_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_docencia_asignada_')],
              # ---
              [sg.Button('Continuar', disabled=True, key='_continuar_'),
               sg.Button('Modificar', disabled=True, key='_modificar_')],
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
              [sg.Button('Aplicar', disabled=True, key='_aplicar_'),
               sg.Button('Cancelar', disabled=True, key='_cancelar_')],
              [sg.T('_' * WIDTH_HLINE)],
              [sg.Button('Salir', key='_salir_')]
              ]

    window = sg.Window("Reparto Docente (FTA)").Layout(layout)

    while True:
        event, values = window.Read()
        print(event, values)
        if event == '_profesor_':
            if values['_profesor_'] == '---':
                window.Element('_encargo_').Update('---')
                window.Element('_asignados_').Update('---')
                window.Element('_diferencia_').Update('---')
                window.Element('_docencia_asignada_').Update('---')
                window.Element('_titulacion_').Update('---')
                window.Element('_continuar_').Update(disabled=True)
            else:
                uuid_profesor = busca_profesor_por_nombre_completo(
                    values['_profesor_'], tabla_profesores
                )
                encargo = tabla_profesores.loc[uuid_profesor]['encargo']
                asignados = tabla_profesores.loc[uuid_profesor]['asignados']
                diferencia = asignados - encargo
                window.Element('_encargo_').Update(round(encargo, 4))
                window.Element('_asignados_').Update(round(asignados, 4))
                window.Element('_diferencia_').Update(round(diferencia, 4))
                window.Element('_continuar_').Update(disabled=False)
        elif event == '_continuar_':
            window.Element('_profesor_').Update(disabled=True)
            window.Element('_continuar_').Update(disabled=True)
            window.Element('_titulacion_').Update(
                values=lista_titulaciones, disabled=False)
            window.Element('_cancelar_').Update(disabled=False)
        elif event == '_titulacion_':
            titulacion = values['_titulacion_']
            if titulacion == '---':
                window.Element('_asignatura_elegida_').Update('---')
                window.Element('_asignatura_elegida_').Update(disabled=True)
                window.Element('_aplicar_').Update(disabled=True)
            else:
                tabla_asignaturas = dict_tablas_asignaturas[titulacion]
                num_asignaturas = tabla_asignaturas.shape[0]
                lista_asignaturas = []
                for i in range(num_asignaturas):
                    dumtxt = tabla_asignaturas['asignatura'][i] + ', ' + \
                             str(round(tabla_asignaturas['creditos'][i], 4)) \
                             + ' créditos'
                    if tabla_asignaturas['comentarios'][i] != ' ':
                        dumtxt += ', ' + tabla_asignaturas['comentarios'][i]
                    if tabla_asignaturas['grupo'][i] != ' ':
                        dumtxt += ', grupo ' + tabla_asignaturas['grupo'][i]
                    lista_asignaturas.append(dumtxt)
                window.Element('_asignatura_elegida_').Update(
                    values=['---'] + lista_asignaturas,
                    disabled=False
                )
        elif event == '_asignatura_elegida_':
            asignatura_elegida = values['_asignatura_elegida_']
            if asignatura_elegida == '---':
                window.Element('_aplicar_').Update(disabled=True)
            else:
                window.Element('_aplicar_').Update(disabled=False)
        elif event == '_aplicar_':
            break
        elif event == '_cancelar_':
            window.Element('_profesor_').Update(
                #values=lista_profesores,
                disabled=False
            )
            window.Element('_titulacion_').Update(
                values='---',
                disabled=True
            )
            window.Element('_asignatura_elegida_').Update(
                values='---',
                disabled=True
            )
            window.Element('_continuar_').Update(disabled=False)
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
