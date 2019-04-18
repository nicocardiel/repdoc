import argparse
import pandas as pd
import PySimpleGUI as sg
import sys

from .date_last_update import datetime_short
from .define_gui_layout import define_gui_layout
from .display_in_terminal import display_in_terminal
from .export_to_html_bitacora import export_to_html_bitacora
from .export_to_html_profesores import export_to_html_profesores
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
from .version import version

from .define_gui_layout import WIDTH_SPACES_FOR_UUID

CREDITOS_ASIGNATURA = 4.5


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
    parser.add_argument("--debug",
                        help="run code in debugging mode",
                        action="store_true")
    parser.add_argument("--echo",
                        help="Display full command line",
                        action="store_true")

    args = parser.parse_args()

    if args.echo:
        print('\033[1m\033[31mExecuting: ' + ' '.join(sys.argv) + '\033[0m\n')

    print('Welcome con RepDoc version ' + version)
    print('Copyright ' + '\u00a9' + ' 2019 Universidad Complutense de Madrid')

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
        # incluye columna con nuevo profesor
        dumtable['nuevo_profesor'] = ' '
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
    tabla_profesores['diferencia'] = \
        tabla_profesores['asignados'] - tabla_profesores['encargo']

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
        if args.web:
            rsync_html_files(args.course)
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
                else:
                    print('* uuid_bita:', uuid_bita)
                    print('* uuid_prof:', uuid_prof)
                    print('* uuid_titu:', uuid_titu)
                    print('* uuid_asig:', uuid_asig)
                    raise ValueError('Error while processing bitacora!')

    # ---
    # export to HTML files

    export_to_html_titulaciones(tabla_titulaciones)
    export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas)
    export_to_html_profesores(tabla_profesores, bitacora)
    if args.web:
        rsync_html_files(args.course)

    # ---
    # GUI

    # set global GUI options
    sg.SetOptions(font=(args.fontname, args.fontsize))

    # define GUI layout
    num_titulaciones = tabla_titulaciones.shape[0]
    layout = define_gui_layout(args.fontsize, num_titulaciones)

    # define GUI window
    window = sg.Window('Reparto Docente (FTA), Curso ' +
                       args.course).Layout(layout)

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

    def comprueba_ronda_profesor(ronda_profesor):
        ronda_actual = int(values['_ronda_'])
        if ronda_actual != 0:
            if ronda_profesor > ronda_actual:
                sg.PopupOK('Se ha superado la ronda actual')

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
                if ronda == 0:
                    umbral = 0.0
                else:
                    umbral = (float(ronda - 1) + 0.5) * CREDITOS_ASIGNATURA
                print('--> ronda............:', ronda)
                print('--> umbral (créditos):', umbral)
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
                ronda_profesor = int(asignados/CREDITOS_ASIGNATURA + 0.5) + 1
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
            dummy = sg.PopupYesNo('¿Seguro que quiere eliminar esta selección')
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
                    bitacora.loc[uuid_bita, 'date_removed'] = \
                        datetime_short()
                # update info for teacher
                encargo = tabla_profesores.loc[uuid_prof]['encargo']
                asignados = tabla_profesores.loc[uuid_prof]['asignados']
                diferencia = tabla_profesores.loc[uuid_prof]['diferencia']
                ronda_profesor = int(asignados/CREDITOS_ASIGNATURA + 0.5) + 1
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
                export_to_html_bitacora(bitacora)
                export_to_html_titulaciones(tabla_titulaciones)
                export_to_html_tablas_asignaturas(bigdict_tablas_asignaturas)
                export_to_html_profesores(tabla_profesores, bitacora)
                if args.web:
                    rsync_html_files(args.course)
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
                            uuid_asig]['creditos_disponibles'], 4)
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
                ronda_profesor = int(asignados/CREDITOS_ASIGNATURA + 0.5) + 1
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
            data_row = [uuid_prof, uuid_titu, uuid_asig,
                        datetime_short(), 'None',
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
            if args.web:
                rsync_html_files(args.course)
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
