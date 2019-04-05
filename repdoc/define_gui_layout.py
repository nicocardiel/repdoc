import PySimpleGUI as sg


WIDTH_HLINE = 90
WIDTH_HLINE_SUMMARY = 62
WIDTH_TEXT_SUMMARY = 18
WIDTH_TEXT_LABEL = 18
WIDTH_TEXT_UUID = 30
WIDTH_INPUT_COMBO = 50
WIDTH_INPUT_NUMBER = 10
WIDTH_INPUT_COMMENT = 50
WIDTH_SPACES_FOR_UUID = 150

COLOR_TITULACIONES = '#AF4CAF'
COLOR_ASIGNATURAS = '#AF4C50'
COLOR_PROFESORES = '#4CAF50'
COLOR_NO_DISPONIBLE = '#555'
COLOR_BITACORA = '#4CAFAF'


def define_gui_layout(fontsize, num_titulaciones):
    """Define GUI layout

    """

    # define monospaced typeface for results
    fontname_header = 'courier bold'
    fontname_no = 'courier'

    layout = [[sg.Text('Titulación',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('iniciales',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('elegidos',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('disponibles',
                       font=(fontname_header, fontsize),
                       text_color='#3333ff',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center'),
               sg.Text('Bec./Col.',
                       font=(fontname_header, fontsize),
                       text_color='#33aa33',
                       size=(WIDTH_TEXT_SUMMARY, 1),
                       justification='center')]]

    for i in range(num_titulaciones):
        clabel = '_{:02d}_'.format(i + 1)
        newrow = [sg.Text('undefined', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_titulacion' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_total' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_elegidos' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_disponibles' + clabel),
                  sg.Text('0.0', font=(fontname_no, fontsize),
                          size=(WIDTH_TEXT_SUMMARY, 1),
                          justification='center',
                          key='_summary_beccol' + clabel)
                  ]
        layout += [newrow]

    layout += [[sg.Text('TOTAL', text_color='#3333ff',
                        font=(fontname_header, fontsize),
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#3333ff',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_total_'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#3333ff',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_elegidos_'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#3333ff',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_disponibles_'),
                sg.Text('0.0', font=(fontname_header, fontsize),
                        text_color='#33aa33',
                        size=(WIDTH_TEXT_SUMMARY, 1),
                        justification='center',
                        key='_summary_beccol_')
                ]]

    layout += [[sg.Checkbox('Excluir elección de asignaturas para '
                            'Becarios/Colaboradores',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_excluir_asignaturas_beccol_')],
               # ---
               [sg.Text('_' * WIDTH_HLINE)],
               # ---
               [sg.Checkbox('Excluir docentes RyC y asimilados',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_excluir_RyC_'),
                sg.Checkbox('Excluir Becarios/Colaboradores',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_excluir_colaboradores_')],
               # ---
               [sg.Text('Nº umbral de créditos:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_umbral_creditos_'),
                sg.InputText(default_text='0.0',
                             size=(WIDTH_INPUT_NUMBER, 1),
                             justification='left',
                             do_not_clear=True, disabled=False,
                             key='_umbral_creditos_'),
                sg.Button('Establecer umbral', key='_establecer_umbral_'),
                sg.Text('(0: selecciona todos los profesores)',
                        text_color='#aaaaaa',
                        auto_size_text=True)],
               # ---
               [sg.Text('_' * WIDTH_HLINE)],
               # ---
               [sg.Text('Nº de profesores seleccionados:',
                        text_color='#aaaaaa', auto_size_text=True),
                sg.Text('0', text_color='#aaaaaa', auto_size_text=True,
                        key='_num_prof_seleccionados_')],
               # ---
               [sg.Text('Profesor/a:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_profesor_'),
                sg.InputCombo(values=['---'],
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              disabled=True, key='_profesor_')],
               # ---
               [sg.Text('Encargo docente:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_encargo_prof_'),
                sg.Text('---', key='_encargo_prof_',
                        size=(WIDTH_TEXT_LABEL, 1))],
               # ---
               [sg.Text('Créditos asignados:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_asignados_prof_'),
                sg.Text('---', key='_asignados_prof_',
                        size=(WIDTH_TEXT_LABEL, 1))],
               # ---
               [sg.Text('Diferencia:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_diferencia_prof_'),
                sg.Text('---', key='_diferencia_prof_',
                        size=(WIDTH_TEXT_LABEL, 1))],
               # ---
               [sg.Text('Docencia asignada:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right',
                        key='_label_docencia_asignada_'),
                sg.InputCombo(values=['---'], disabled=True,
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              key='_docencia_asignada_')],
               # ---
               [sg.Button('Continuar', disabled=True, key='_continuar_'),
                sg.Button('Eliminar', disabled=True, key='_eliminar_')],
               [sg.Text('_' * WIDTH_HLINE)],
               # ---
               [sg.Text('Titulación:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right', key='_label_titulacion_'),
                sg.InputCombo(values=['---'], disabled=True,
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              key='_titulacion_')],
               # ---
               [sg.Text('Asignatura elegida:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right',
                        key='_label_asignatura_elegida_'),
                sg.InputCombo(values=['---'], disabled=True,
                              size=(WIDTH_INPUT_COMBO, 1), enable_events=True,
                              key='_asignatura_elegida_')],
               # ---
               [sg.Text('', size=(WIDTH_TEXT_LABEL, 1)),
                sg.Checkbox('Todos los créditos',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_fraccion_todo_',
                            disabled=True),
                sg.Checkbox('Solo una parte',
                            default=False,
                            change_submits=True,
                            auto_size_text=True,
                            key='_fraccion_parte_',
                            disabled=True),
                sg.Text('Créditos a elegir:', text_color="#aaaaaa",
                        auto_size_text=True,
                        key='_label_creditos_elegidos_'),
                sg.InputText(default_text='0.0', text_color="#aaaaaa",
                             size=(WIDTH_INPUT_NUMBER, 1),
                             justification='left',
                             do_not_clear=True, disabled=True,
                             key='_creditos_elegidos_')],
               # ---
               [sg.Text('Explicación:', size=(WIDTH_TEXT_LABEL, 1),
                        justification='right',
                        key='_label_explicacion_'),
                sg.InputText(default_text=' ',
                             size=(WIDTH_INPUT_COMMENT, 1),
                             justification='left',
                             do_not_clear=True, disabled=True,
                             key='_explicacion_')],
               # ---
               [sg.Button('Aplicar', disabled=True, key='_aplicar_'),
                sg.Button('Cancelar', disabled=True, key='_cancelar_')],
               [sg.Text('_' * WIDTH_HLINE)],
               [sg.Button('Salir', key='_salir_')]
               ]

    return layout
