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


def read_tabla_asignaturas(tabla_titulacion, debug=False):
    """Read csv files with subjects.

    """

    tabla_asignaturas = pd.read_csv(
        tabla_titulacion,
        skiprows=5,
        sep=";",
        header=None,
        usecols=range(10),
        names=['curso', 'semestre', 'codigo', 'asignatura', 'area', 'uuid',
               'creditos', 'comentarios', 'grupo', 'profesor_anterior']
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

    # convert to integer
    for item in ['semestre', 'codigo']:
        tabla_asignaturas[item] = tabla_asignaturas[item].apply(
            lambda f: int(f)
        )

    # convert creditos into float (e.g. "1,6" -> 1.6)
    tabla_asignaturas['creditos'] = tabla_asignaturas['creditos'].apply(
        lambda s: float(s.replace(',', '.'))
    )

    if(debug):
        print(tabla_asignaturas)
        print('Créditos totales:', tabla_asignaturas['creditos'].sum())
        input("Stop here!")

    return tabla_asignaturas


def read_tabla_profesores(teachers_csv_file, debug=False):
    """Read csv file with teachers participating in the assignment round.

    """

    tabla_profesores = pd.read_csv(
        teachers_csv_file,
        skiprows=2,
        sep=';',
        header=None,
        usecols=[0, 1, 2, 3, 17],
        names=['uuid', 'apellidos', 'nombre', 'categoria', 'encargo']
    )

    # remove unnecessary rows
    lok = tabla_profesores['uuid'].notnull()
    tabla_profesores = tabla_profesores[lok]

    # reset index values
    tabla_profesores = tabla_profesores.reset_index(drop=True)

    # convert encargo into float (e.g. "1,6" -> 1.6)
    tabla_profesores['encargo'] = tabla_profesores['encargo'].apply(
        lambda s: float(s.replace(',', '.'))
    )

    if debug:
        print(tabla_profesores)
        print('Encargo total:', tabla_profesores['encargo'].sum())
        input('Stop here!')

    return tabla_profesores


def main(args=None):

    # parse command-line options
    parser = argparse.ArgumentParser(description='Subject assignment tool')

    parser.add_argument("teachers",
                        help="CSV file with teacher lists",
                        type=argparse.FileType('rt'))
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

    tabla_titulaciones = pd.DataFrame(
        data={'label': ['Grado en Física', 'Grado en IEC', 'Otros Grados',
                        'Másteres'],
              'csvfile': ['grado_en_fisica', 'grado_en_iec', 'otros_grados',
                          'masteres']})

    tabla_asignaturas_grado_en_fisica = read_tabla_asignaturas(
        'asignaturas_' + tabla_titulaciones['csvfile'][0] + '.csv',
        debug=args.debug
    )

    tabla_asignaturas_grado_en_iec = read_tabla_asignaturas(
        'asignaturas_' + tabla_titulaciones['csvfile'][1] + '.csv',
        debug=args.debug
    )

    tabla_profesores = read_tabla_profesores(
        args.teachers,
        debug=args.debug
    )

    num_profesores = tabla_profesores.shape[0]

    list_profesores = ['---'] + \
                      [tabla_profesores['nombre'][i] + ' ' +
                       tabla_profesores['apellidos'][i]
                       for i in range(num_profesores)]

    list_titulaciones = ['?',
                         'Grado en Física',
                         'Grado en IEC',
                         'Otros grados',
                         'Másteres'
                         ]

    list_asignaturas_grado_fisica = ['?',
                                     'Fundamentos de Física I',
                                     'Matemáticas',
                                     'LCC'
                                     ]
    list_asignaturas_grado_iec = ['?', 'Álgebra']
    list_asignaturas_otros_grados = ['?',
                                     'Física para Biólogos',
                                     'Física para Geólogos'
                                     ]
    list_asignaturas_masteres = ['?',
                                 'Atmósferas Estelares',
                                 'Dinámica de Galaxias'
                                 'Meteorología 1',
                                 'Geofísica 2',
                                 'Geofísica avanzada'
                                 ]

    sg.SetOptions(font=(args.fontname, args.fontsize))

    layout = [[sg.T('Resumen...')],
              [sg.T('_' * WIDTH_HLINE)],
              [sg.T('Profesor/a:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_profesor_'),
               sg.InputCombo(values=list_profesores,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_profesor_')],
              [sg.T('Encargo docente:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_encargo_docente_'),
               sg.T('---', key='_encargo_docente_')],
              [sg.T('Créditos asignados:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_creditos_asignados_'),
               sg.T('---', key='_creditos_asignados_')],
              [sg.T('Diferencia:', size=(
                  WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_diferencia_'),
               sg.T('---', key='_diferencia_')],
              [sg.T('Docencia asignada:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_docencia_asignada_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_docencia_asignada_')],
              [sg.Button('Continuar', disabled=True),
               sg.Button('Modificar', disabled=True)],
              [sg.T('_' * WIDTH_HLINE)],
              [sg.T('Titulación:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_titulacion_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_titulacion_')],
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
            window.Element('_profesor_').Update(values=list_profesores)
            window.Element('_titulacion_').Update(values='---', disabled=True)
            window.Element('_asignatura_').Update(values='---', disabled=True)
        elif event == "Aplicar":
            break
        elif event == '_profesor_':
            if values['_profesor_'] != '?':
                window.Element('_titulacion_').Update(values=list_titulaciones, disabled=False)
        elif event == '_titulacion_':
            if values['_titulacion_'] != '?':
                window.Element('_asignatura_').Update(disabled=False)
            if values['_titulacion_'] == 'Grado en Física':
                window.Element('_asignatura_').Update(values=list_asignaturas_grado_fisica)
            elif values['_titulacion_'] == 'Grado en IEC':
                window.Element('_asignatura_').Update(values=list_asignaturas_grado_iec)
            elif values['_titulacion_'] == 'Otros grados':
                window.Element('_asignatura_').Update(values=list_asignaturas_otros_grados)
            elif values['_titulacion_'] == 'Másteres':
                window.Element('_asignatura_').Update(values=list_asignaturas_masteres)

    window.Close()


if __name__ == "__main__":

    main()
