import os.path

FONT_PATH = os.path.join('res', 'fonts')
FONT_CONFIG_EXTENSION = '.font.json'

window_dimensions = None
tile_dimensions = None
mouse_position = None

def parse_text_into_characters(text):
    characters = []
    is_escaping = False
    group = None
    def append(ch):
        """append the next character to the right place"""
        if group is None:
            characters.append(ch)
        else:
            group.append(ch)

    for ch in text:
        if ch == '\\':
            if is_escaping:
                append(ch)
                is_escaping = False
            else:
                is_escaping = True
        elif ch == '[':
            if is_escaping:
                append(ch)
                is_escaping = False
            else:
                if group is not None:
                    raise ValueError('You cannot start a character group within another group.')
                group = []
            is_escaping = False
        elif ch == ']':
            if is_escaping:
                append(ch)
            else:
                if group is None:
                    raise ValueError('You cannot end a character group that you have not started.')
                if len(group) == 0:
                    raise ValueError('You cannot have an empty character group.')
                characters.append(''.join(group))
                group = None
            is_escaping = False
        else:
            if is_escaping:
                raise ValueError("Invalid escape character '" + ch + "'.")
            append(ch)
            is_escaping = False
    if is_escaping:
        raise ValueError("The '\\' at the end of the string isn't escaping anything.")
    if group is not None:
        raise ValueError('You started a character group but did not finish it.')
    return characters
