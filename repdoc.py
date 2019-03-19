import argparse
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import sys


WIDTH_HLINE = 90
WIDTH_TEXT_LABEL = 18
WIDTH_TEXT_UUID = 30
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

    # asignaturas de cada titulacion
    if args.course == '2019-2020':
        skiprows=5
        usecols=range(1,11)
    else:
        raise ValueError("Unexpected course!")
    bigdict_tablas_asignaturas = {}
    for titulacion in tabla_titulaciones['titulacion']:
        bigdict_tablas_asignaturas[titulacion] = read_tabla_asignaturas(
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

    sg.SetOptions(font=(args.fontname, args.fontsize))

    layout = [[sg.Text('Resumen...')],
              [sg.Text('_' * WIDTH_HLINE)],
              # ---
              [sg.Text('Nº umbral de créditos:', size=(WIDTH_TEXT_LABEL, 1),
                       justification='right', key='_label_umbral_creditos_'),
               sg.InputText(default_text='0.0',
                            size=(WIDTH_INPUT_NUMBER, 1),
                            justification='left',
                            do_not_clear=True, disabled=False,
                            key='_umbral_creditos_'),
               sg.Button('Establecer umbral', key='_establecer_umbral_')],
              # ---
              [sg.Text('_' * WIDTH_HLINE)],
              # ---
              [sg.Text('Profesor/a:', size=(WIDTH_TEXT_LABEL,1),
                       justification='right', key='_label_profesor_'),
               sg.InputCombo(values=['---'],
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             disabled=True,
                             key='_profesor_')],
              # ---
              [sg.Text('', size=(WIDTH_TEXT_LABEL, 1)),
               sg.Text('uuid:', text_color="#aaaaaa", auto_size_text=True,
                       key='_label_uuid_profesor_'),
               sg.InputText('---', text_color="#aaaaaa",
                            size=(WIDTH_TEXT_UUID, 1),
                            disabled=True, do_not_clear=True,
                            key='_uuid_profesor_')],
              # ---
              [sg.Text('Encargo docente:', size=(WIDTH_TEXT_LABEL,1),
                       justification='right', key='_label_encargo_'),
               sg.Text('---', key='_encargo_', size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.Text('Créditos asignados:', size=(WIDTH_TEXT_LABEL,1),
                       justification='right', key='_label_asignados_'),
               sg.Text('---', key='_asignados_', size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.Text('Diferencia:', size=(WIDTH_TEXT_LABEL,1),
                       justification='right', key='_label_diferencia_'),
               sg.Text('---', key='_diferencia_', size=(WIDTH_TEXT_LABEL, 1))],
              # ---
              [sg.Text('Docencia asignada:', size=(WIDTH_TEXT_LABEL,1),
                       justification='right', key='_label_docencia_asignada_'),
               sg.InputCombo(values=['---'], disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_docencia_asignada_')],
              # ---
              [sg.Button('Continuar', disabled=True, key='_continuar_'),
               sg.Button('Eliminar', disabled=True, key='_eliminar_')],
              [sg.Text('_' * WIDTH_HLINE)],
              # ---
              [sg.Text('Titulación:', size=(WIDTH_TEXT_LABEL,1),
                       justification='right', key='_label_titulacion_'),
               sg.InputCombo(values=['---'], disabled=True,
                             size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                             key='_titulacion_')],
              # ---
              [sg.Text('', size=(WIDTH_TEXT_LABEL, 1)),
               sg.Text('uuid:', text_color="#aaaaaa", auto_size_text=True,
                       key='_label_uuid_titulacion_'),
               sg.InputText('---', text_color="#aaaaaa",
                            size=(WIDTH_TEXT_UUID, 1),
                            disabled=True, do_not_clear=True,
                            key='_uuid_titulacion_')],
              # ---
              [sg.Text('Asignatura elegida:', size=(WIDTH_TEXT_LABEL, 1),
                       justification='right',
                       key='_label_asignatura_elegida_'),
               sg.InputCombo(values=['---'], disabled=True,
                             size=(WIDTH_INPUT_COMBO,1), enable_events=True,
                             key='_asignatura_elegida_')],
              # ---
              [sg.Text('', size=(WIDTH_TEXT_LABEL, 1)),
               sg.Text('uuid:', text_color="#aaaaaa", auto_size_text=True,
                       key='_label_uuid_asignatura_'),
               sg.InputText('---', text_color="#aaaaaa",
                            size=(WIDTH_TEXT_UUID, 1),
                            disabled=True, do_not_clear=True,
                            key='_uuid_asignatura_')],
              # ---
              [sg.Text('', size=(WIDTH_TEXT_LABEL, 1)),
               sg.Checkbox('Todos los créditos',
                           default=False,
                           change_submits=True,
                           auto_size_text=True,
                           key='_fraccion_de_asignatura_todo_',
                           disabled=True),
               sg.Checkbox('Solo una parte',
                           default=False,
                           change_submits=True,
                           auto_size_text=True,
                           key='_fraccion_de_asignatura_parte_',
                           disabled=True),
               sg.Text('Créditos a elegir:', text_color="#aaaaaa",
                       auto_size_text=True,
                       key='_label_creditos_elegidos_de_asignatura_'),
               sg.InputText(default_text='0.0', text_color="#aaaaaa",
                            size=(WIDTH_INPUT_NUMBER, 1),
                            justification='left',
                            do_not_clear=True, disabled=True,
                            key='_creditos_elegidos_de_asignatura_')],
              # ---
              [sg.Button('Aplicar', disabled=True, key='_aplicar_'),
               sg.Button('Cancelar', disabled=True, key='_cancelar_')],
              [sg.Text('_' * WIDTH_HLINE)],
              [sg.Button('Salir', key='_salir_')]
              ]

    window = sg.Window("Reparto Docente (FTA)").Layout(layout)

    uuid_profesor = None
    uuid_titulacion = None
    uuid_lista_asignaturas = None
    uuid_asignatura = None
    creditos_max_asignatura = 0.0

    while True:
        event, values = window.Read()
        print(event, values)
        if event == '_establecer_umbral_':
            lista_profesores = ['---']
            umbral_is_float = True
            umbral = 0.0  # avoid warning
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
                    num_profesores = tabla_profesores.shape[0]
                    for i in range(num_profesores):
                        nombre_completo = tabla_profesores['nombre'][i] + ' ' + \
                                          tabla_profesores['apellidos'][i]
                        if umbral == 0:
                            lista_profesores.append(nombre_completo)
                        elif tabla_profesores['asignados'][i] < umbral:
                            lista_profesores.append(nombre_completo)
            window.Element('_profesor_').Update(
                values=lista_profesores,
                disabled=False
            )
            window.Element('_uuid_profesor_').Update('---')
            window.Element('_encargo_').Update('---')
            window.Element('_asignados_').Update('---')
            window.Element('_diferencia_').Update('---')
            window.Element('_docencia_asignada_').Update('---')
            window.Element('_titulacion_').Update('---')
            window.Element('_continuar_').Update(disabled=True)
            window.Element('_eliminar_').Update(disabled=True)
            window.Element('_titulacion_').Update(
                values='---',
                disabled=True
            )
            window.Element('_asignatura_elegida_').Update(
                values='---',
                disabled=True
            )
            window.Element('_aplicar_').Update(disabled=True)
            window.Element('_cancelar_').Update(disabled=True)
        elif event == '_profesor_':
            if values['_profesor_'] == '---':
                window.Element('_encargo_').Update('---')
                window.Element('_asignados_').Update('---')
                window.Element('_diferencia_').Update('---')
                window.Element('_docencia_asignada_').Update('---')
                window.Element('_titulacion_').Update('---')
                window.Element('_continuar_').Update(disabled=True)
                window.Element('_eliminar_').Update(disabled=True)
                uuid_profesor = None
                window.Element('_uuid_profesor_').Update('---')
            else:
                uuid_profesor = busca_profesor_por_nombre_completo(
                    values['_profesor_'], tabla_profesores
                )
                window.Element('_uuid_profesor_').Update(uuid_profesor)
                encargo = tabla_profesores.loc[uuid_profesor]['encargo']
                asignados = tabla_profesores.loc[uuid_profesor]['asignados']
                diferencia = asignados - encargo
                window.Element('_encargo_').Update(round(encargo, 4))
                window.Element('_asignados_').Update(round(asignados, 4))
                window.Element('_diferencia_').Update(round(diferencia, 4))
                window.Element('_continuar_').Update(disabled=False)
        elif event == '_continuar_':
            if uuid_profesor is None:
                raise ValueError('Unexpected uuid_profesor == None')
            print('* Profesor elegido:', tabla_profesores.loc[uuid_profesor])
            window.Element('_profesor_').Update(disabled=True)
            window.Element('_continuar_').Update(disabled=True)
            lista_titulaciones = ['---'] + \
                                 tabla_titulaciones['titulacion'].tolist()
            window.Element('_titulacion_').Update(
                values=lista_titulaciones, disabled=False)
            window.Element('_cancelar_').Update(disabled=False)
        elif event == '_titulacion_':
            titulacion = values['_titulacion_']
            if titulacion == '---':
                uuid_titulacion = None
                uuid_lista_asignaturas = None
                window.Element('_uuid_titulacion_').Update('---')
                window.Element('_asignatura_elegida_').Update('---')
                window.Element('_asignatura_elegida_').Update(disabled=True)
                window.Element('_uuid_asignatura_').Update('---')
                window.Element('_fraccion_de_asignatura_todo_').Update(
                    value=False, disabled=True
                )
                window.Element('_fraccion_de_asignatura_parte_').Update(
                    value=False, disabled=True
                )
                window.Element('_creditos_elegidos_de_asignatura_').Update(
                    str(0.0)
                )
                window.Element('_aplicar_').Update(disabled=True)
            else:
                uuid_titulacion = tabla_titulaciones.loc[
                    tabla_titulaciones['titulacion'] == titulacion
                ].index.values[0]
                window.Element('_uuid_titulacion_').Update(uuid_titulacion)
                tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
                num_asignaturas = tabla_asignaturas.shape[0]
                lista_asignaturas = []
                uuid_lista_asignaturas = {}
                for i in range(num_asignaturas):
                    dumtxt = tabla_asignaturas['asignatura'][i] + ', ' + \
                             str(round(tabla_asignaturas['creditos'][i], 4)) \
                             + ' créditos'
                    if tabla_asignaturas['comentarios'][i] != ' ':
                        dumtxt += ', ' + tabla_asignaturas['comentarios'][i]
                    if tabla_asignaturas['grupo'][i] != ' ':
                        dumtxt += ', grupo ' + tabla_asignaturas['grupo'][i]
                    lista_asignaturas.append(dumtxt)
                    uuid_lista_asignaturas[dumtxt] = tabla_asignaturas.index[i]
                window.Element('_asignatura_elegida_').Update(
                    values=['---'] + lista_asignaturas,
                    disabled=False
                )
        elif event == '_asignatura_elegida_':
            asignatura_elegida = values['_asignatura_elegida_']
            if asignatura_elegida == '---':
                uuid_asignatura = None
                window.Element('_uuid_asignatura_').Update('---')
                window.Element('_fraccion_de_asignatura_todo_').Update(
                    value=False, disabled=True
                )
                window.Element('_fraccion_de_asignatura_parte_').Update(
                    value=False, disabled=True
                )
                window.Element('_creditos_elegidos_de_asignatura_').Update(
                    str(0.0)
                )
                window.Element('_aplicar_').Update(disabled=True)
            else:
                uuid_asignatura = uuid_lista_asignaturas[asignatura_elegida]
                window.Element('_uuid_asignatura_').Update(uuid_asignatura)
                print('* uuid_profesor..:', uuid_profesor)
                print('* uuid_titulacion:', uuid_titulacion)
                print('* uuid_asignatura:', uuid_asignatura)
                titulacion = values['_titulacion_']
                creditos_max_asignatura = bigdict_tablas_asignaturas[
                    titulacion].loc[uuid_asignatura]['creditos']
                window.Element('_fraccion_de_asignatura_todo_').Update(
                    disabled=False
                )
                window.Element('_fraccion_de_asignatura_parte_').Update(
                    disabled=False
                )
                window.Element('_creditos_elegidos_de_asignatura_').Update(
                    str(round(bigdict_tablas_asignaturas[
                                  titulacion].loc[uuid_asignatura]['creditos'], 4))
                )
        elif event == '_fraccion_de_asignatura_todo_':
            window.Element('_fraccion_de_asignatura_todo_').Update(
                value=True
            )
            window.Element('_fraccion_de_asignatura_parte_').Update(
                value=False
            )
            window.Element('_label_creditos_elegidos_de_asignatura_').Update(
                text_color="#aaaaaa"
            )
            window.Element('_creditos_elegidos_de_asignatura_').Update(
                value=str(round(creditos_max_asignatura, 4)),
                disabled=True,
            )
            window.Element('_aplicar_').Update(disabled=False)
        elif event == '_fraccion_de_asignatura_parte_':
            window.Element('_fraccion_de_asignatura_todo_').Update(
                value=False
            )
            window.Element('_fraccion_de_asignatura_parte_').Update(
                value=True
            )
            loop = True
            creditos_elegidos_de_asignatura = \
                values['_creditos_elegidos_de_asignatura_']
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
                        creditos_elegidos_de_asignatura = float(dumtxt)
                    except ValueError:
                        sg.Popup('ERROR', 'Número inválido')
                        lfloat = False
                    if lfloat:
                        if 0 < creditos_elegidos_de_asignatura < limite_maximo:
                            loop = False
                        else:
                            sg.Popup('ERROR',
                                     '¡Número fuera del intervalo válido!\n' +
                                     '0 < valor < ' + str(limite_maximo))
            window.Element('_creditos_elegidos_de_asignatura_').Update(
                           str(float(creditos_elegidos_de_asignatura))
            )
            window.Element('_aplicar_').Update(disabled=False)
        elif event == '_aplicar_':
            print('* uuid_profesor..: ' +
                  window.Element('_uuid_profesor_').Get())
            print('* uuid_titulacion: ' +
                  window.Element('_uuid_titulacion_').Get())
            print('* uuid_asignatura: ' +
                  window.Element('_uuid_asignatura_').Get())
            print('* creditos.......: ' +
                  str(values['_creditos_elegidos_de_asignatura_']))
        elif event == '_cancelar_':
            window.Element('_profesor_').Update(disabled=False)
            window.Element('_continuar_').Update(disabled=False)
            window.Element('_titulacion_').Update(
                values='---',
                disabled=True
            )
            window.Element('_uuid_titulacion_').Update('---')
            window.Element('_asignatura_elegida_').Update(
                values='---',
                disabled=True
            )
            window.Element('_uuid_asignatura_').Update('---')
            window.Element('_fraccion_de_asignatura_todo_').Update(
                value=False, disabled=True
            )
            window.Element('_fraccion_de_asignatura_parte_').Update(
                value=False, disabled=True
            )
            window.Element('_creditos_elegidos_de_asignatura_').Update(
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
