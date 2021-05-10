#
# Copyright 2019-2021 Universidad Complutense de Madrid
#
# This file is part of RepDoc
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSE.txt
#

from .definitions import CREDITOS_ASIGNATURA
from .definitions import FLAG_RONDA_NO_ELIGE
from .definitions import PRIMERA_RONDA_RYC


def update_ronda_profesor(tabla_profesores, uuid_prof):
    """Actualiza ronda siguiente del profesor"""

    encargo = tabla_profesores.loc[uuid_prof]['encargo']
    categoria = tabla_profesores.loc[uuid_prof]['categoria']
    if (encargo == 0) or (categoria == 'Colaborador'):
        ronda_profesor = FLAG_RONDA_NO_ELIGE
    else:
        ronda_profesor = int(
            tabla_profesores.loc[uuid_prof]['asignados'] /
            CREDITOS_ASIGNATURA + 0.5
        ) + 1
        if ('RyC' in tabla_profesores.loc[uuid_prof]['categoria']) or \
                ('JdC' in tabla_profesores.loc[uuid_prof]['categoria']):
            ronda_profesor += (PRIMERA_RONDA_RYC - 1)
            if ronda_profesor < PRIMERA_RONDA_RYC:
                ronda_profesor = PRIMERA_RONDA_RYC

    tabla_profesores.loc[
        uuid_prof, 'ronda'
    ] = ronda_profesor
