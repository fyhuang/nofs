def next_json(stream):
    bracket_level = 0
    in_string = False

    result = []
    while True:
        b = stream.read(1)
        if bracket_level > 0:
            result += [b]
        if b == '{':
            result += ['{']
            bracket_level += 1
        elif b == '}':
            bracket_level -= 1
            if bracket_level == 0:
                return ''.join(result)
