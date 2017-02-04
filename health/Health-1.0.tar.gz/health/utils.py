from codes import icd2desc

def find_codes(search_word):
    codes = {}
    for code, desc in icd2desc.iteritems():
        if search_word in desc.lower():
            codes[code] = desc
    return codes


if __name__ == '__main__':
    print find_codes('fish')
