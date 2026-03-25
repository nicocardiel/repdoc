#
# Copyright 2019-2026 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .define_gui_layout import WIDTH_SPACES_FOR_UUID


def filtra_asignaturas(tabla_asignaturas,
                       excluir_asignaturas_beccol=False):
    """Return list with subjects with available credits.

    """

    num_asignaturas = tabla_asignaturas.shape[0]
    lista_asignaturas = []
    for i in range(num_asignaturas):
        if excluir_asignaturas_beccol:
            if tabla_asignaturas['bec_col'].iloc[i] == 1:
                incluir_asignatura = False
            else:
                incluir_asignatura = True
        else:
            incluir_asignatura = True
        if incluir_asignatura:
            if tabla_asignaturas['creditos_disponibles'].iloc[i] > 0:
                dumtxt = '{:2d}. '.format(tabla_asignaturas['num'].iloc[i])
                dumtxt += '[' + tabla_asignaturas['curso'].iloc[i] + '] '
                dumtxt += tabla_asignaturas['asignatura'].iloc[i] + ', '
                dumtxt += str(
                    round(tabla_asignaturas['creditos_disponibles'].iloc[i], 4)
                ) + ' créditos'
                if tabla_asignaturas['comentarios'].iloc[i] != ' ':
                    dumtxt += ', ' + tabla_asignaturas['comentarios'].iloc[i]
                if tabla_asignaturas['grupo'].iloc[i] != ' ':
                    dumtxt += ', grupo ' + tabla_asignaturas['grupo'].iloc[i]
                ldum = len(dumtxt)
                if ldum < WIDTH_SPACES_FOR_UUID:
                    dumtxt += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
                dumtxt += '  --> uuid_asig=' + tabla_asignaturas.index[i]
                lista_asignaturas.append(dumtxt)

    return lista_asignaturas
