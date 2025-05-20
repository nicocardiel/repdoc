#
# Copyright 2019-2025 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import argparse
from datetime import datetime
import os
import pandas as pd
import platform
import PySimpleGUI as sg
import sys

from .ctext import ctext
from .date_last_update import datetime_short
from .define_gui_layout import define_gui_layout
from .display_in_terminal import display_in_terminal
from .export_to_html_bitacora import export_to_html_bitacora
from .export_to_html_index import export_to_html_index
from .export_to_html_profesores import export_to_html_profesores
from .export_to_html_resultado import export_to_html_resultado
from .export_to_html_tablas_asignaturas import \
    export_to_html_tablas_asignaturas
from .export_to_html_titulaciones import export_to_html_titulaciones
from .filtra_asignaturas import filtra_asignaturas
from .filtra_seleccion_del_profesor import filtra_seleccion_del_profesor
from .filtra_titulaciones import filtra_titulaciones
from .new_uuid import new_uuid
from .read_tabla_asignaturas import read_tabla_asignaturas
from .read_tabla_profesores import read_tabla_profesores
from .read_tabla_titulaciones import read_tabla_titulaciones
from .rsync_html_files import rsync_html_files
from .update_ronda_profesor import update_ronda_profesor
from .version import version

from .define_gui_layout import WIDTH_SPACES_FOR_UUID

from .definitions import DEFAULT_BITACORA_XLSX_FILENAME
from .definitions import CREDITOS_ASIGNATURA
from .definitions import FLAG_RONDA_NO_ELIGE
from .definitions import NULL_UUID
from .definitions import PRIMERA_RONDA_RYC
from .definitions import ROUND_ERROR
from .definitions import TEXT_ACTIVA_ELECCION
from .definitions import TEXT_FINALIZA_ELECCION


def main(args=None):

    # parse command-line options
    parser = argparse.ArgumentParser(description='Subject assignment tool')

    parser.add_argument("xlsxfile",
                        help="Excel file with input data",
                        type=argparse.FileType())
    parser.add_argument("--course", required=True,
                        help="Academic course (e.g. 2019-2020)",
                        type=str)
    parser.add_argument("--bitacora",
                        help="CSV input/output filename",
                        type=argparse.FileType())
    parser.add_argument("--warning_collaborators",
                        help="Warning when available credits for "
                             "collaborators falls bellow provided limit",
                        default=0.0,
                        type=float)
    parser.add_argument('--web',
                        help="rsync HTML files in web server",
                        action="store_true")
    parser.add_argument("--fontname",
                        help="font name for GUI",
                        default='Helvetica',
                        type=str)
    parser.add_argument("--fontsize",
                        help="font name for GUI",
                        default=12,
                        type=int)
    parser.add_argument("--theme",
                        help="PySimpleGUI theme",
                        default="SandyBeach",
                        type=str)
    parser.add_argument("--debug",
                        help="run code in debugging mode",
                        action="store_true")
    parser.add_argument("--echo",
                        help="Display full command line",
                        action="store_true")

    args = parser.parse_args()

    if args.course in ['2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']:
        raise SystemExit(f'The course {args.course} is blocked. No changes allowed.')

    execution_command = ' '.join(sys.argv)
    if args.echo:
        print(ctext(f'Executing: {execution_command}', fg='red', bold=True))
    with open('last_execution_command.txt', 'a') as f:
        f.write('-' * 79)
        f.write(f'\n{datetime.now()}\n')
        f.write(f'{platform.uname().node}\n')
        f.write(f'{execution_command}\n')

    print(ctext(f'Welcome to RepDoc version {version}', bold=True))
    copyright_symbol = '\u00a9'
    print(f'Copyright {copyright_symbol} 2019-2025 Universidad Complutense de Madrid')
    print('\nLoading tables (please wait):')

    global warning_collaborators
    if args.warning_collaborators > 0:
        warning_collaborators = args.warning_collaborators
    else:
        warning_collaborators = 0.0

    # ---
    # load Excel sheets
    # ---

    # variable para almacenar los UUIDs de titulaciones, asignaturas
    # y profesores
    megalist_uuid = []

    # ---
    # titulaciones
    print(ctext('\n-> Updating subjects', fg='green', bold=True))
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

    # ---
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
        # incluye columna con nuevo profesor
        dumtable['nuevo_profesor'] = ' '
        # incluye columna con créditos disponibles
        dumtable['creditos_disponibles'] = dumtable['creditos_iniciales']
        # incluye número de fila en la tabla
        dumtable['num'] = 0
        for irow, uuid_asig in enumerate(dumtable.index):
            dumtable.loc[uuid_asig, 'num'] = irow + 1
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

    # ---
    # profesores
    print(ctext('\n-> Updating teachers', fg='green', bold=True))
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
    tabla_profesores['diferencia'] = \
        tabla_profesores['asignados'] - tabla_profesores['encargo']
    tabla_profesores['ronda'] = 0  # force column to be integer
    tabla_profesores['finalizado'] = False
    tabla_profesores['num'] = 0
    for iprof, uuid_prof in enumerate(tabla_profesores.index):
        tabla_profesores.loc[uuid_prof, 'num'] = iprof + 1
        categoria = tabla_profesores.loc[uuid_prof]['categoria']
        creditos_encargo = tabla_profesores.loc[uuid_prof]['encargo']
        if categoria in ['Colaborador', 'Colaboradora']:
            tabla_profesores.loc[uuid_prof, 'ronda'] = FLAG_RONDA_NO_ELIGE
        elif creditos_encargo == 0:
            tabla_profesores.loc[uuid_prof, 'ronda'] = FLAG_RONDA_NO_ELIGE
            tabla_profesores.loc[uuid_prof, 'finalizado'] = True
        else:
            if 'RyC' in categoria or 'JdC' in categoria:
                tabla_profesores.loc[uuid_prof, 'ronda'] = PRIMERA_RONDA_RYC
            else:
                tabla_profesores.loc[uuid_prof, 'ronda'] = 1

    # comprueba que los UUIDs de titulaciones, asignaturas y profesores
    # son todos distintos
    if len(megalist_uuid) != len(set(megalist_uuid)):
        for dumuuid in megalist_uuid:
            if megalist_uuid.count(dumuuid) > 1:
                print(dumuuid)
        raise ValueError('UUIDs are not unique when mixing everything!')

    # ---
    # define bitacora
    csv_colnames_profesor = ['apellidos', 'nombre', 'categoria']
    csv_colnames_asignatura = ['curso', 'semestre', 'codigo', 'asignatura',
                               'area', 'creditos_iniciales', 'comentarios',
                               'grupo']
    csv_colvalues_asignatura_null = ['-', 0, 0, '-',
                                     '-', 0.0, '-',
                                     '-']
    print(ctext('\n-> Updating bitacora', fg='green', bold=True))
    if args.bitacora is None:
        # check that there is not a file with the expected name
        # (in order to avoid overwriting it)
        if os.path.isfile(DEFAULT_BITACORA_XLSX_FILENAME):
            raise ValueError('File ' + DEFAULT_BITACORA_XLSX_FILENAME +
                             ' already exists!')
        # initialize empty dataframe with the expected columns
        bitacora = pd.DataFrame(
            data=[],
            columns=['uuid_prof', 'uuid_titu', 'uuid_asig',
                     'date_added', 'round_added',
                     'date_removed', 'round_removed',
                     'creditos_elegidos', 'explicacion'] +
                    csv_colnames_profesor + csv_colnames_asignatura
        )
        bitacora.index.name = 'uuid_bita'
        if args.debug:
            print('Initialasing bitacora DataFrame:')
            print(bitacora)
            input('Press <CR> to continue...')
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
            uuid_prof = bitacora.loc[uuid_bita]['uuid_prof']
            uuid_titu = bitacora.loc[uuid_bita]['uuid_titu']
            # activate/deactivate teacher
            if uuid_titu == NULL_UUID:
                explicacion = bitacora.loc[uuid_bita]['explicacion']
                if explicacion == TEXT_FINALIZA_ELECCION:
                    tabla_profesores.loc[uuid_prof, 'finalizado'] = True
                elif explicacion == TEXT_ACTIVA_ELECCION:
                    tabla_profesores.loc[uuid_prof, 'finalizado'] = False
                else:
                    raise ValueError('Unexpected explicacion for null UUID')
                status = False
            else:
                status = str(bitacora.loc[uuid_bita]['date_removed']) == 'None'
            # apply selected subject
            if status:
                uuid_asig = bitacora.loc[uuid_bita]['uuid_asig']
                creditos_elegidos = \
                    bitacora.loc[uuid_bita]['creditos_elegidos']
                asignacion_es_correcta = True
                titulacion = tabla_titulaciones.loc[uuid_titu]['titulacion']
                tabla_asignaturas = bigdict_tablas_asignaturas[titulacion]
                if tabla_asignaturas.loc[
                    uuid_asig, 'creditos_disponibles'
                ] >= creditos_elegidos - ROUND_ERROR:
                    tabla_asignaturas.loc[
                        uuid_asig, 'creditos_disponibles'
                    ] -= creditos_elegidos
                    if abs(tabla_asignaturas.loc[
                               uuid_asig, 'creditos_disponibles'
                           ]) < ROUND_ERROR:
                        tabla_asignaturas.loc[
                            uuid_asig, 'creditos_disponibles'
                        ] = 0
                    nuevo_profesor = \
                        tabla_profesores.loc[uuid_prof]['nombre'] + ' ' + \
                        tabla_profesores.loc[uuid_prof]['apellidos']
                    if bool(
                        tabla_asignaturas.loc[
                            uuid_asig, 'nuevo_profesor'
                        ].strip()
                    ):
                        tabla_asignaturas.loc[uuid_asig, 'nuevo_profesor'] += \
                            ' + ' + nuevo_profesor
                    else:
                        tabla_asignaturas.loc[uuid_asig, 'nuevo_profesor'] = \
                            nuevo_profesor
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
                    update_ronda_profesor(tabla_profesores, uuid_prof)
                else:
                    print('* uuid_bita:', uuid_bita)
                    print('* uuid_prof:', uuid_prof)
                    print('* uuid_titu:', uuid_titu)
                    print('* uuid_asig:', uuid_asig)
                    raise ValueError('Error while processing bitacora!')

    # ---
    # export to HTML files
    export_to_html_index(args.course)
    export_to_html_bitacora(bitacora, args.bitacora, args.course)
    export_to_html_titulaciones(tabla_titulaciones, args.course)
    export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas,
                                      args.course)
    export_to_html_profesores(tabla_profesores, bitacora, 0, args.course)
    export_to_html_resultado(tabla_profesores, bigdict_tablas_asignaturas,
                             bitacora, args.course)
    if args.web:
        rsync_html_files(args.course, args.xlsxfile, args.bitacora)

    # ---
    # GUI

    # set global GUI options
    sg.SetOptions(font=(args.fontname, args.fontsize))

    # set theme (it must be done before defining the layout)
    # use the following code to display available options:
    #    import PySimpleGUI as sg
    #    sg.theme_previewer()
    sg.theme(args.theme)    # Another good option is 'Default'

    # define GUI layout
    num_titulaciones = tabla_titulaciones.shape[0]
    layout = define_gui_layout(args.fontname, args.fontsize, num_titulaciones)

    # define GUI window
    window = sg.Window(
        'Reparto Docente (FTA), Curso ' + args.course,
        use_default_focus=False
    ).Layout(layout)

    # ---
    # define auxiliary functions

    def clear_screen_profesor(profesor_disabled=True):
        if profesor_disabled:
            window.Element('_profesor_').Update(values='---', disabled=True)
            window.Element('_num_prof_seleccionados_').Update('0')
            window.Element('_ronda_profesor_').Update('---')
        window.Element('_encargo_prof_').Update('---')
        window.Element('_asignados_prof_').Update('---')
        window.Element('_diferencia_prof_').Update('---')
        window.Element('_docencia_asignada_').Update('---', disabled=True)
        window.Element('_titulacion_').Update('---')
        window.Element('_continuar_').Update(disabled=True)
        window.Element('_eliminar_').Update(disabled=True)
        window.Element('_profesor_finalizado_').Update(disabled=True)

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
        window.Element('_confirmar_').Update(disabled=True)
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
            clabel = f'_{i + 1:02d}_'
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

        global warning_collaborators
        if warning_collaborators > 0.0:
            if total_disponibles_beccol <= warning_collaborators:
                msg = 'Se ha alcanzado el límite de créditos\nprereservados para PIF'
                print(ctext(msg + '\nclick [OK]', bg='red'))
                sg.PopupOK(msg)
                ### sg.PopupOK(msg, auto_close=True, auto_close_duration=5)
                warning_collaborators = 0.0

    def comprueba_ronda_profesor(ronda_profesor):
        ronda_actual = int(values['_ronda_'])
        if ronda_actual != 0:
            if ronda_profesor > ronda_actual:
                msg = 'Se ha superado la ronda actual'
                print(ctext(msg + '\nclick [OK]', bg='yellow'))
                sg.PopupOK(msg)
                ### sg.PopupOK(msg, auto_close=True, auto_close_duration=2)

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
        elif event == '_ronda_':
            clear_screen_asignatura()
            clear_screen_profesor()
        # ---
        elif event == '_establecer_ronda_':
            lista_profesores = ['---']
            num_profesores = 0
            try:
                ronda = int(values['_ronda_'])
            except ValueError:
                sg.Popup('ERROR', 'Número de ronda inválido')
                ronda = None
            if ronda is not None:
                if ronda >= FLAG_RONDA_NO_ELIGE:
                    sg.Popup('ERROR', 'Número de ronda inválido')
                    ronda = None
            if ronda is not None:
                if ronda == 0:
                    umbral = 0.0
                else:
                    umbral = (float(ronda - 1) + 0.5) * CREDITOS_ASIGNATURA
                print('--> ronda............:', ronda)
                print('--> umbral (créditos):', umbral)
                for uuid_prof in tabla_profesores.index:
                    iprof = tabla_profesores.loc[uuid_prof]['num']
                    nombre_completo = \
                        f'{iprof:2d}. ' + \
                        tabla_profesores.loc[uuid_prof]['nombre'] + ' ' + \
                        tabla_profesores.loc[uuid_prof]['apellidos']
                    ldum = len(nombre_completo)
                    if ldum < WIDTH_SPACES_FOR_UUID:
                        nombre_completo += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                    nombre_completo += '  --> uuid_prof=' + uuid_prof
                    if ronda == 0:
                        num_profesores += 1
                        lista_profesores.append(nombre_completo)
                    elif tabla_profesores.loc[uuid_prof]['ronda'] <= ronda:
                        if not tabla_profesores.loc[uuid_prof]['finalizado']:
                            num_profesores += 1
                            lista_profesores.append(nombre_completo)
                export_to_html_profesores(tabla_profesores, bitacora, ronda,
                                          args.course)
                if args.web:
                    rsync_html_files(args.course, args.xlsxfile, args.bitacora)
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
                ronda_profesor = tabla_profesores.loc[uuid_prof]['ronda']
                window.Element('_ronda_profesor_').Update(ronda_profesor)
                comprueba_ronda_profesor(ronda_profesor)
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(
                    round(diferencia, 4)
                )
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
                if tabla_profesores.loc[uuid_prof]['finalizado']:
                    window.Element('_continuar_').Update(disabled=True)
                    window.Element('_profesor_finalizado_').Update(
                        text='Activar elección en rondas'
                    )
                else:
                    window.Element('_continuar_').Update(disabled=False)
                    window.Element('_profesor_finalizado_').Update(
                        text='Finalizar elección en rondas'
                    )
                window.Element('_profesor_finalizado_').Update(disabled=False)
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
            window.Element('_profesor_finalizado_').Update(disabled=True)
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
            msg = '¿Seguro que quiere eliminar esta selección (y/n)? '
            dummy = sg.PopupYesNo(msg)
            print(dummy)
            print(dummy.lower())
            ### dummy = input(ctext(msg, bg='green'))
            if dummy.lower() in ['y', 'yes']:
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
                    update_ronda_profesor(tabla_profesores, uuid_prof)
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
                    nuevo_profesor = \
                        tabla_profesores.loc[uuid_prof]['nombre'] + ' ' + \
                        tabla_profesores.loc[uuid_prof]['apellidos']
                    tabla_asignaturas.loc[uuid_asig, 'nuevo_profesor'] += \
                        ' - ' + nuevo_profesor
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
                    ronda_actual = int(values['_ronda_'])
                    bitacora.loc[uuid_bita, 'date_removed'] = datetime_short()
                    bitacora.loc[uuid_bita, 'round_removed'] = ronda_actual
                # update info for teacher
                encargo = tabla_profesores.loc[uuid_prof]['encargo']
                asignados = tabla_profesores.loc[uuid_prof]['asignados']
                diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
                ronda_profesor = tabla_profesores.loc[uuid_prof]['ronda']
                window.Element('_ronda_profesor_').Update(ronda_profesor)
                comprueba_ronda_profesor(ronda_profesor)
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(
                    round(diferencia, 4)
                )
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
                export_to_html_bitacora(bitacora, args.bitacora, args.course)
                export_to_html_titulaciones(tabla_titulaciones, args.course)
                export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas,
                                                  args.course)
                ronda_actual = int(values['_ronda_'])
                export_to_html_profesores(tabla_profesores, bitacora,
                                          ronda_actual, args.course)
                export_to_html_resultado(tabla_profesores,
                                         bigdict_tablas_asignaturas,
                                         bitacora, args.course)
                if args.web:
                    rsync_html_files(args.course, args.xlsxfile, args.bitacora)
        # ---
        elif event == '_profesor_finalizado_':
            uuid_prof = values['_profesor_'][-36:]
            if uuid_prof is None:
                raise ValueError('Unexpected uuid_prof == None')
            #
            if tabla_profesores.loc[uuid_prof]['finalizado']:
                window.Element('_profesor_finalizado_').Update(
                    text='Finalizar elección en rondas'
                )
                tabla_profesores.loc[uuid_prof, 'finalizado'] = False
                window.Element('_continuar_').Update(disabled=False)
                explicacion = TEXT_ACTIVA_ELECCION
            else:
                window.Element('_profesor_finalizado_').Update(
                    text='Activar elección en rondas'
                )
                tabla_profesores.loc[uuid_prof, 'finalizado'] = True
                window.Element('_continuar_').Update(disabled=True)
                explicacion = TEXT_FINALIZA_ELECCION
            #
            # prepare new entry for bitacora
            uuid_bita = str(new_uuid(megalist_uuid))
            uuid_titu = NULL_UUID
            uuid_asig = NULL_UUID
            creditos_elegidos = 0.0
            ronda_actual = int(values['_ronda_'])
            data_row = [uuid_prof, uuid_titu, uuid_asig,
                        datetime_short(), ronda_actual,
                        'None', 'None',
                        creditos_elegidos, explicacion]
            for item in csv_colnames_profesor:
                data_row.append(tabla_profesores.loc[uuid_prof][item])
            for idum in range(len(csv_colnames_asignatura)):
                data_row.append(csv_colvalues_asignatura_null[idum])
            new_entry = pd.DataFrame(data=[data_row],
                                     index=[uuid_bita],
                                     columns=bitacora.columns.tolist())
            bitacora = pd.concat([bitacora, new_entry])
            bitacora.index.name = 'uuid_bita'
            if args.debug:
                print(bitacora)
            export_to_html_bitacora(bitacora, args.bitacora, args.course)
            ronda_actual = int(values['_ronda_'])
            export_to_html_profesores(tabla_profesores, bitacora,
                                      ronda_actual, args.course)
            if args.web:
                rsync_html_files(args.course, args.xlsxfile, args.bitacora)
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
                window.Element('_confirmar_').Update(disabled=True)
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
                window.Element('_confirmar_').Update(disabled=True)
            else:
                uuid_titu = values['_titulacion_'][-36:]
                uuid_asig = values['_asignatura_elegida_'][-36:]
                titulacion = tabla_titulaciones.loc[uuid_titu][
                    'titulacion']
                creditos_max_asignatura = bigdict_tablas_asignaturas[
                    titulacion].loc[uuid_asig]['creditos_disponibles']
                antiguedad_asignatura_str = bigdict_tablas_asignaturas[
                    titulacion].loc[uuid_asig]['antiguedad']
                profesor_anterior = bigdict_tablas_asignaturas[
                    titulacion].loc[uuid_asig]['profesor_anterior']
                try:
                    antiguedad_asignatura = float(antiguedad_asignatura_str)
                    warning_antiguedad = (antiguedad_asignatura >= 6)
                except:
                    warning_antiguedad = True
                if warning_antiguedad:
                    info = f'Antigüedad: {antiguedad_asignatura_str} cursos\n'
                    info += f'Profesor/a anterior: {profesor_anterior}'
                    print(ctext(info + '\nclick [OK]', bg='red'))
                    sg.PopupOK(info)
                    ### sg.PopupOK(info, auto_close=True, auto_close_duration=5)
                window.Element('_fraccion_todo_').Update(
                    value=False, disabled=False
                )
                window.Element('_fraccion_parte_').Update(
                    value=False, disabled=False
                )
                window.Element('_creditos_elegidos_').Update(
                    str(round(
                        bigdict_tablas_asignaturas[titulacion].loc[
                            uuid_asig]['creditos_disponibles'], 4)
                    )
                )
                window.Element('_confirmar_').Update(disabled=True)
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
            window.Element('_confirmar_').Update(disabled=False)
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
                msg = f'¿Créditos a elegir (0 < valor < {round(limite_maximo, 5)})? '
                dumtxt = sg.PopupGetText(msg, '¿Créditos?')
                ### sg.Popup(msg, auto_close=True, auto_close_duration=3)
                ### dumtxt = input(ctext(msg, bg='green'))
                print(dumtxt, type(dumtxt))
                if dumtxt is None:
                    loop = False
                else:
                    lfloat = True
                    try:
                        creditos_elegidos = float(dumtxt)
                    except ValueError:
                        msg = '¡Número inválido!'
                        print(ctext(msg, bg='red'))
                        ### sg.Popup('ERROR', msg, auto_close=True, auto_close_duration=5)
                        lfloat = False
                    if lfloat:
                        if 0 < creditos_elegidos < limite_maximo:
                            loop = False
                        else:
                            msg = f'¡Número fuera del intervalo válido!\n0 < valor < {limite_maximo}'
                            print(ctext(msg, bg='red'))
                            ### sg.Popup('ERROR', msg, auto_close=True, auto_close_duration=5)
            window.Element('_creditos_elegidos_').Update(
                           str(float(creditos_elegidos))
            )
            window.Element('_explicacion_').Update(
                value=' ', disabled=False
            )
            window.Element('_confirmar_').Update(disabled=False)
        # ---
        elif event == '_confirmar_':
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
                ] > creditos_elegidos - ROUND_ERROR:
                    tabla_asignaturas.loc[
                        uuid_asig, 'creditos_disponibles'
                    ] -= creditos_elegidos
                    if abs(tabla_asignaturas.loc[
                               uuid_asig, 'creditos_disponibles'
                           ]) < ROUND_ERROR:
                        tabla_asignaturas.loc[
                            uuid_asig, 'creditos_disponibles'
                        ] = 0
                else:
                    print('¡Créditos disponibles insuficientes!')
                    input('Press <CR> to continue...')
                    asignacion_es_correcta = False
            else:
                print('¡Fracción de asignatura no establecida!')
                input('Press <CR> to continue...')
                asignacion_es_correcta = False
            if asignacion_es_correcta:
                nuevo_profesor = \
                    tabla_profesores.loc[uuid_prof]['nombre'] + ' ' + \
                    tabla_profesores.loc[uuid_prof]['apellidos']
                if bool(
                        tabla_asignaturas.loc[
                            uuid_asig, 'nuevo_profesor'
                        ].strip()
                ):
                    tabla_asignaturas.loc[uuid_asig, 'nuevo_profesor'] += \
                        ' + ' + nuevo_profesor
                else:
                    tabla_asignaturas.loc[uuid_asig, 'nuevo_profesor'] = \
                        nuevo_profesor
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
                update_ronda_profesor(tabla_profesores, uuid_prof)
                ronda_profesor = tabla_profesores.loc[uuid_prof]['ronda']
                window.Element('_ronda_profesor_').Update(ronda_profesor)
                comprueba_ronda_profesor(ronda_profesor)
                window.Element('_encargo_prof_').Update(round(encargo, 4))
                window.Element('_asignados_prof_').Update(round(asignados, 4))
                window.Element('_diferencia_prof_').Update(
                    round(diferencia, 4)
                )
            # Nota: uuid_bita tendrá un valor único para cada elección de los
            # profesores. Esto permite discriminar dentro de una misma
            # asignatura (i.e., mismo uuid_prof, uuid_titu,
            # uuid_asig) cuando se eligen fracciones de asignatura (es
            # decir, cuando se subdividen asignaturas por un mismo profesor)
            uuid_bita = str(new_uuid(megalist_uuid))
            megalist_uuid += [uuid_bita]
            # prepare new entry for bitacora
            ronda_actual = int(values['_ronda_'])
            data_row = [
                uuid_prof, uuid_titu, uuid_asig,
                datetime_short(), ronda_actual,
                'None', 'None', creditos_elegidos, values['_explicacion_']
            ]
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
            window.Element('_profesor_finalizado_').Update(disabled=False)
            export_to_html_bitacora(bitacora, args.bitacora, args.course)
            export_to_html_titulaciones(tabla_titulaciones, args.course)
            export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas,
                                              args.course)
            ronda_actual = int(values['_ronda_'])
            export_to_html_profesores(tabla_profesores, bitacora,
                                      ronda_actual, args.course)
            export_to_html_resultado(tabla_profesores,
                                     bigdict_tablas_asignaturas,
                                     bitacora, args.course)
            if args.web:
                rsync_html_files(args.course, args.xlsxfile, args.bitacora)
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
                coption = input(ctext('Do you really want to exit (y/n) [y] ? ', bg='red'))
                if coption == '':
                    coption = 'y'
                if coption != 'y' and coption != 'n':
                    print('Invalid answer. Try again!')
            if coption == 'y':
                break

    window.Close()


if __name__ == "__main__":

    main()
