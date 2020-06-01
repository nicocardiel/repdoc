#
# Copyright 2019-2020 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .define_gui_layout import WIDTH_SPACES_FOR_UUID


def filtra_titulaciones(tabla_titulaciones):
    """Return list with degrees with available credits.

    """

    num_titulaciones = tabla_titulaciones.shape[0]
    lista_titulaciones = []
    for i in range(num_titulaciones):
        if tabla_titulaciones['creditos_disponibles'][i] > 0:
            nombre_titulacion = tabla_titulaciones['titulacion'][i]
            ldum = len(nombre_titulacion)
            if ldum < WIDTH_SPACES_FOR_UUID:
                nombre_titulacion += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
            nombre_titulacion += ' uuid_titu=' + tabla_titulaciones.index[i]
            lista_titulaciones.append(nombre_titulacion)

    return lista_titulaciones
