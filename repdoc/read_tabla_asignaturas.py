import pandas as pd

from .fill_cell_with_previous_value import fill_cell_with_previous_value
from .str_nonan import str_nonan


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
        sumproduct = \
            tabla_asignaturas['creditos_iniciales'] * \
            tabla_asignaturas['bec_col']
        print('Créditos posibles para becarios/colaboradores:',
              round(sumproduct.sum(), 3))
        input("Press <CR> to continue...")

    return tabla_asignaturas