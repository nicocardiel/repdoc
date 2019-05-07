#
# Copyright 2019 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import pandas as pd


def read_tabla_profesores(xlsxfilename, course, debug=False):
    """Lee hoja Excel con lista de profesores que participan en rondas

    """

    if course == '2019-2020':
        sheet_name = 'Asignación'
        skiprows = 7
        usecols = [0, 1, 2, 3, 19]
        names = ['uuid_prof', 'apellidos', 'nombre', 'categoria',
                 'encargo']
        converters = {'uuid_prof': str,
                      'apellidos': str,
                      'nombre': str,
                      'categoria': str,
                      'encargo': float}
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
        raise ValueError('UUIDs are not unique!')

    if debug:
        print(tabla_profesores)
        print('Encargo total:', tabla_profesores['encargo'].sum())
        input('Press <CR> to continue...')

    return tabla_profesores
