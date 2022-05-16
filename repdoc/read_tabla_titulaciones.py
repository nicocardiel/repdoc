#
# Copyright 2019-2022 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

import pandas as pd


def read_tabla_titulaciones(xlsxfilename, course, debug=False):
    """Lee hoja Excel con lista de titulaciones.

    """

    if course in ['2019-2020', '2020-2021', '2021-2022', '2022-2023']:
        sheet_name = 'Resumen Encargo'
        skiprows = 4
        usecols = [1, 2]
        names = ['uuid_titu', 'titulacion']
        converters = {'uuid_titu': str, 'titulacion': str}
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
    lok = tabla_inicial['uuid_titu'].notnull()
    tabla_inicial = tabla_inicial[lok]

    # reset index values
    tabla_inicial = tabla_inicial.reset_index(drop=True)

    # use uuid as index
    tabla_titulaciones = tabla_inicial.copy()
    tabla_titulaciones.index = tabla_inicial['uuid_titu']
    del tabla_titulaciones['uuid_titu']

    # check that uuid's are unique
    if len(tabla_titulaciones.index) != len(set(tabla_titulaciones.index)):
        dumlist = tabla_titulaciones.index.tolist()
        duplicates = set([item for item in dumlist if dumlist.count(item) > 1])
        for item in duplicates:
            print(tabla_titulaciones.loc[item])
        raise ValueError('UUIDs are not unique!')

    if debug:
        print(tabla_titulaciones)
        input('Press <CR> to continue...')

    return tabla_titulaciones
