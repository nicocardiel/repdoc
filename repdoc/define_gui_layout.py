import PySimpleGUI as sg


WIDTH_HLINE = 110
WIDTH_HLINE_SUMMARY = 62
WIDTH_TEXT_SUMMARY = 18
WIDTH_TEXT_LABEL = 18
WIDTH_TEXT_UUID = 30
WIDTH_INPUT_COMBO_CORTO = 50
WIDTH_INPUT_COMBO = 75
WIDTH_INPUT_NUMBER = 10
WIDTH_INPUT_COMMENT = 50
WIDTH_SPACES_FOR_UUID = 150

COLOR_ASIGNACION_HEAD = '#5C1B68'
COLOR_ASIGNACION_EVEN = '#EECFF3'
COLOR_ASIGNACION_ODD = '#FAF0FC'
COLOR_ASIGNATURAS_HEAD = '#A71614'
COLOR_ASIGNATURAS_EVEN = '#FCD9D6'
COLOR_ASIGNATURAS_ODD = '#FEF4F3'
COLOR_BITACORA_HEAD = '#985C13'
COLOR_BITACORA_EVEN = '#FEEACD'
COLOR_BITACORA_ODD = '#FFF9F0'
COLOR_TITULACIONES_HEAD = '#306732'
COLOR_TITULACIONES_EVEN = '#DBEEDC'
COLOR_TITULACIONES_ODD = '#F4FAF4'
COLOR_PROFESORES_HEAD = '#26326B'
COLOR_PROFESORES_EVEN = '#D8DCF0'
COLOR_PROFESORES_ODD = '#F3F4FB'
COLOR_NO_DISPONIBLE = '#999'


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
               [sg.Text('Ronda:', key='_label_ronda_'),
                sg.Spin([i for i in range(100)],
                        initial_value=0,
                        change_submits=True,
                        key='_ronda_'),
                sg.Text('(0: selecciona todos los profesores)',
                        text_color='#aaaaaa',
                        auto_size_text=True),
                sg.Button('Establecer ronda', key='_establecer_ronda_')],
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
                              size=(WIDTH_INPUT_COMBO_CORTO, 1),
                              enable_events=True,
                              disabled=True, key='_profesor_'),
                sg.Text('Próxima ronda:',
                        key='_label_ronda_profesor_'),
                sg.Text('---', key='_ronda_profesor_')],
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
                              size=(WIDTH_INPUT_COMBO_CORTO, 1),
                              enable_events=True,
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
