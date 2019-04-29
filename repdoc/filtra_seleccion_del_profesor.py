from .define_gui_layout import WIDTH_SPACES_FOR_UUID
from .definitions import NULL_UUID


def filtra_seleccion_del_profesor(uuid_prof, bitacora):
    """Return list with subjects already assigned to a teacher.

    """

    output = ['---']

    # subset of bitacora for the selected teacher
    seleccion = bitacora.loc[
        (bitacora['uuid_prof'] == uuid_prof) &
        (bitacora['date_removed'] == 'None')
    ].copy()

    # find how many times the selected teacher appears
    ntimes = seleccion.shape[0]
    if ntimes == 0:
        return output

    for i in range(ntimes):
        if seleccion['uuid_titu'].tolist()[i] != NULL_UUID:
            dumtxt = '[' + seleccion['curso'].tolist()[i] + '] '
            dumtxt += seleccion['asignatura'].tolist()[i] + ', '
            dumtxt += str(
                round(seleccion['creditos_elegidos'].tolist()[i], 4)
            ) + ' créditos'
            if seleccion['comentarios'].tolist()[i] != ' ':
                dumtxt += ', ' + seleccion['comentarios'].tolist()[i]
            if seleccion['grupo'].tolist()[i] != ' ':
                dumtxt += ', grupo ' + seleccion['grupo'].tolist()[i]
            ldum = len(dumtxt)
            if ldum < WIDTH_SPACES_FOR_UUID:
                dumtxt += (WIDTH_SPACES_FOR_UUID - ldum) * ' '
            dumtxt += ' uuid_bita=' + seleccion.index.tolist()[i]
            output.append(dumtxt)

    return output
