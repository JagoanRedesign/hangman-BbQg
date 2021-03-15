def format_string(string):
    line_replace = ['~', '`', '>', '#', '+', '-', '=', '|', '.', '!']
    for line in line_replace:
        string = string.replace(line, f'\\{line}')
    return string

