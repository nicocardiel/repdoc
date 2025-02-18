#
# Copyright 2019-2023 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import pandas as pd

from .ctext import ctext
from .definitions import VALID_COURSES

def read_tabla_profesores(xlsxfilename, course, debug=False):
    """Lee hoja Excel con lista de profesores que participan en rondas

    """

    if course in VALID_COURSES:
        sheet_name = 'Asignación'
        skiprows = 7
        names = ['uuid_prof', 'apellidos', 'nombre', 'categoria', 'encargo']
        # indicate column numbers for the previous labels
        if course == '2019-2020':
            usecols = [0, 1, 2, 3, 19]
        elif course == '2020-2021':
            usecols = [0, 1, 2, 3, 21]
        elif course == '2021-2022':
            usecols = [0, 2, 3, 4, 23]
        elif course in ['2022-2023', '2023-2024', '2024-2025']:
            usecols = [0, 2, 3, 4, 19]
        else:
            raise SystemExit(f'Invalid course: {course}')
        converters = {'uuid_prof': str,
                      'apellidos': str,
                      'nombre': str,
                      'categoria': str,
                      'encargo': float}
    else:
        print('Course: ' + course)
        raise ValueError('Unexpected course!')

    if debug:
        print(ctext(f'\nReading {xlsxfilename}', fg='blue'))
        print('Sheet: "' + sheet_name + '"')

    # print(ctext('WARNING> step1', bg='red', fg='white'))
    tabla_inicial = pd.read_excel(
        xlsxfilename,
        sheet_name=sheet_name,
        skiprows=skiprows,
        header=None,
        usecols=usecols,
        names=names,
        converters=converters,
    )
    # print(ctext('WARNING> step2', bg='red', fg='white'))

    # remove unnecessary rows
    lok = tabla_inicial['uuid_prof'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_profesores = tabla_inicial.copy()
    tabla_profesores.index = tabla_inicial['uuid_prof']
    del tabla_profesores['uuid_prof']

    # check that uuid's are unique
    if len(tabla_profesores.index) != len(set(tabla_profesores.index)):
        dumlist = tabla_profesores.index.tolist()
        duplicates = set([item for item in dumlist if dumlist.count(item) > 1])
        for item in duplicates:
            print(tabla_profesores.loc[item])
        raise ValueError('UUIDs are not unique!')

    if debug:
        print(tabla_profesores)
        print('Encargo total:', tabla_profesores['encargo'].sum())
        input('Press <CR> to continue...')

    return tabla_profesores
