from .definitions import CREDITOS_ASIGNATURA
from .definitions import PRIMERA_RONDA_RYC


def update_ronda_profesor(tabla_profesores, uuid_prof):
    """Actualiza ronda siguiente del profesor"""

    if tabla_profesores.loc[uuid_prof]['encargo'] == 0:
        ronda_profesor = 99
    else:
        ronda_profesor = int(
            tabla_profesores.loc[uuid_prof]['asignados'] /
            CREDITOS_ASIGNATURA + 0.5
        ) + 1
        if 'RyC' in tabla_profesores.loc[uuid_prof]['categoria']:
            if ronda_profesor < PRIMERA_RONDA_RYC:
                ronda_profesor = PRIMERA_RONDA_RYC

    tabla_profesores.loc[
        uuid_prof, 'ronda'
    ] = ronda_profesor
