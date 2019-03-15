import argparse
import pandas as pd
import PySimpleGUI as sg
import sys


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
    list_profesores = [tabla_profesores['nombre'][i] + ' ' +
                       tabla_profesores['apellidos'][i]
                       for i in range(num_profesores)
                       ]

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

    layout = [[sg.T('Profesor/a:', size=(15,1), key='_label_profesor_'),
               sg.InputCombo(values=list_profesores,
                             size=(40,1), enable_events=True, key='_profesor_')],
              [sg.T('Titulación:', size=(15,1), key='_label_titulacion_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(40,1), enable_events=True, key='_titulacion_')],
              [sg.T('Asignatura:', size=(15,1), key='_label_asignatura_'),
               sg.InputCombo(values='---', disabled=True,
                             size=(40,1), enable_events=True, key='_asignatura_')],
              [sg.Button('Aplicar'), sg.Button('Cancelar')]
              ]

    window = sg.Window("Reparto Docente (FTA)").Layout(layout)

    while True:
        event, values = window.Read()
        print(event, values)
        if event is None:
            break
        elif event == "Cancelar":
            window.FindElement('_profesor_').Update(values=list_profesores)
            window.FindElement('_titulacion_').Update(values='---', disabled=True)
            window.FindElement('_asignatura_').Update(values='---', disabled=True)
        elif event == "Aplicar":
            break
        elif event == '_profesor_':
            if values['_profesor_'] != '?':
                window.FindElement('_titulacion_').Update(values=list_titulaciones, disabled=False)
        elif event == '_titulacion_':
            if values['_titulacion_'] != '?':
                window.FindElement('_asignatura_').Update(disabled=False)
            if values['_titulacion_'] == 'Grado en Física':
                window.FindElement('_asignatura_').Update(values=list_asignaturas_grado_fisica)
            elif values['_titulacion_'] == 'Grado en IEC':
                window.FindElement('_asignatura_').Update(values=list_asignaturas_grado_iec)
            elif values['_titulacion_'] == 'Otros grados':
                window.FindElement('_asignatura_').Update(values=list_asignaturas_otros_grados)
            elif values['_titulacion_'] == 'Máster en Astrofísica':
                window.FindElement('_asignatura_').Update(values=list_asignaturas_master_astrofisica)
            elif values['_titulacion_'] == 'Máster en Meteorología y Geofísica':
                window.FindElement('_asignatura_').Update(values=list_asignaturas_master_meteogeo)
            elif values['_titulacion_'] == 'Máster en Energía':
                window.FindElement('_asignatura_').Update(values=list_asignaturas_master_energia)

    window.Close()


if __name__ == "__main__":

    main()
