import time

def next_json(stream):
    bracket_level = 0
    in_string = False

    result = []
    while True:
        b = stream.read(1)
        if len(b) < 1:
            # end of stream
            return None
        #print(b)

        if bracket_level > 0:
            result += [b]
        if b == b'{':
            result += [b'{']
            bracket_level += 1
        elif b == b'}':
            bracket_level -= 1
            if bracket_level == 0:
                return (b'').join(result)
