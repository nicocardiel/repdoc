def display_in_terminal(event, values):
    """Show 'event' and 'values' in the terminal

    """

    print("\nEvent: '" + str(event) + "'")
    for key in values:
        output = "    '" + key + "': "
        if isinstance(values[key], str):
            if values[key][-46:-42] == 'uuid':
                output += "'" + values[key][:-46].rstrip() + " ... " + \
                          values[key][-46:] + "'"
            else:
                output += "'" + values[key] + "'"
        else:
            output += str(values[key])
        print(output)
