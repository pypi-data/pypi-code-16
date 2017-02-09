from codes import icd2desc, ccs2desc

def find_codes(search_word, kind='icd'):
    if kind == 'icd':
        code_dict = icd2desc
    else:
        code_dict = ccs2desc

    search_word = search_word.lower()
    codes = {}
    for code, desc in code_dict.iteritems():
        if search_word in desc.lower():
            codes[code] = desc
    return codes


if __name__ == '__main__':
    print find_codes('heart', 'ccs')
