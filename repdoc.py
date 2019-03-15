import argparse
import pandas as pd
import PySimpleGUI as sg
import sys


WIDTH_HLINE = 90
WIDTH_TEXT_LABEL = 20
WIDTH_INPUT_COMBO = 50
WIDTH_BEFORE_EXIT_BUTTON = 55


def read_tabla_profesores(teachers_csv_file, debug=False):
    """Read csv file with teachers participating in the assignment round.

    """

    teachers_table = pd.read_csv(teachers_csv_file,
                                 skiprows=2, sep=';', header=None,
                                 usecols=[0, 1, 2, 3, 17],
                                 names=['uuid', 'apellidos', 'nombre',
                                        'categoria', 'encargo']
                                 )

    # remove unnecessary rows
    lok = teachers_table['uuid'].notnull()
    teachers_table = teachers_table[lok]

    # reset index values
    teachers_table = teachers_table.reset_index(drop=True)

    if debug:
        print(teachers_table)
        input('Stop here!')

    return teachers_table


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

    tabla_profesores = read_tabla_profesores(args.teachers, debug=args.debug)
    num_profesores = tabla_profesores.shape[0]
    list_profesores = ['---'] + \
                      [tabla_profesores['nombre'][i] + ' ' +
                       tabla_profesores['apellidos'][i]
                       for i in range(num_profesores)]

    list_titulaciones = ['?',
                         'Grado en Física',
                         'Grado en IEC',
                         'Otros grados',
                         'Máster en Astrofísica',
                         'Máster en Meteorología y Geofísica',
                         'Máster en Energía'
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
    list_asignaturas_master_astrofisica = ['?',
                                           'Atmósferas Estelares',
                                           'Dinámica de Galaxias'
                                           ]
    list_asignaturas_master_meteogeo = ['?',
                                        'Meteorología 1',
                                        'Geofísica 2',
                                        'Geofísica avanzada'
                                        ]
    list_asignaturas_master_energia = ['?',
                                       'La única que hay'
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
               sg.T('---')],
              [sg.T('Créditos asignados:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_creditos_asignados_'),
               sg.T('---')],
              [sg.T('Diferencia:', size=(
                  WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_diferencia_'),
               sg.T('---')],
              [sg.T('Docencia asignada:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right',
                    key='_label_docencia_asignada_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_docencia_elegida_')],
              [sg.Button('Continuar', disabled=True),
               sg.Button('Modificar', disabled=True)],
              [sg.T('_' * WIDTH_HLINE)],
              [sg.T('Titulación:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_titulacion_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_titulacion_')],
              [sg.T('Asignatura:', size=(WIDTH_TEXT_LABEL,1),
                    justification='right', key='_label_asignatura_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_asignatura_')],
              [sg.T('', size=(WIDTH_TEXT_LABEL,1)),
               sg.Radio('Todos los créditos', '_fraccion_asignatura_',
                        default=True, size=(WIDTH_TEXT_LABEL,1),
                        disabled=True),
               sg.Radio('Solo una parte', '_fraccion_asignatura_',
                        default=False, size=(WIDTH_TEXT_LABEL,1),
                        disabled=True)],
              [sg.Button('Aplicar', disabled=True),
               sg.Button('Cancelar', disabled=True),
               sg.T(' ', size=(WIDTH_BEFORE_EXIT_BUTTON,1)),
               sg.Button('Salir')]
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
            elif values['_titulacion_'] == 'Máster en Astrofísica':
                window.Element('_asignatura_').Update(values=list_asignaturas_master_astrofisica)
            elif values['_titulacion_'] == 'Máster en Meteorología y Geofísica':
                window.Element('_asignatura_').Update(values=list_asignaturas_master_meteogeo)
            elif values['_titulacion_'] == 'Máster en Energía':
                window.Element('_asignatura_').Update(values=list_asignaturas_master_energia)

    window.Close()


if __name__ == "__main__":

    main()
