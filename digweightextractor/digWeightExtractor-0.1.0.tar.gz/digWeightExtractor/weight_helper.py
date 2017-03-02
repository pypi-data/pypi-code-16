# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-22 17:52:30
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-11-11 13:38:45

import re

######################################################################
#   Constant
######################################################################

# Constants for weight
WEIGHT_UNIT_POUND = 'pound'
WEIGHT_UNIT_KILOGRAM = 'kilogram'

WEIGHT_UNIT_POUND_ABBRS = ['lb', 'lbs']
WEIGHT_UNIT_KILOGRAM_ABBRS = ['kg']

WEIGHT_UNITS_DICT = {
    WEIGHT_UNIT_POUND: WEIGHT_UNIT_POUND_ABBRS,
    WEIGHT_UNIT_KILOGRAM: WEIGHT_UNIT_KILOGRAM_ABBRS
}

# Transform
WEIGHT_TRANSFORM_DICT = {
    (WEIGHT_UNIT_POUND, WEIGHT_UNIT_POUND): 1,
    (WEIGHT_UNIT_POUND, WEIGHT_UNIT_KILOGRAM): 0.45359237,
    (WEIGHT_UNIT_KILOGRAM, WEIGHT_UNIT_POUND): 2.2046,
    (WEIGHT_UNIT_KILOGRAM, WEIGHT_UNIT_KILOGRAM): 1,
}


######################################################################
#   Regular Expression
######################################################################

reg_us_weight_unit_lb = r'\b\d{2,3}[ ]*(?:lb|lbs)\b'
reg_us_weight_unit_kg = r'\b\d{2}[ ]*kg\b'

re_us_weight = re.compile(r'(?:' + r'|'.join([
    reg_us_weight_unit_lb,
    reg_us_weight_unit_kg
]) + r')', re.IGNORECASE)

reg_ls_weight = r'(?<=weight)[: \n]*' + r'(?:' + r'|'.join([
    reg_us_weight_unit_lb,
    reg_us_weight_unit_kg,
    r'(?:\d{1,3})'
]) + r')'

re_ls_weight = re.compile(reg_ls_weight, re.IGNORECASE)

######################################################################
#   Main Class
######################################################################


class WeightHelper(object):

    ######################################################################
    #   Clean
    ######################################################################
    @staticmethod
    def clean_extraction(extraction):
        extraction = extraction.replace(':', '')
        extraction = extraction.lower().strip()
        return extraction

    @staticmethod
    def remove_dups(extractions):
        return [dict(_) for _ in set([tuple(dict_item.items()) for dict_item in extractions if dict_item])]

    ######################################################################
    #   Normalize
    ######################################################################
    @staticmethod
    def normalize_weight(extraction):
        extraction = WeightHelper.clean_extraction(extraction)
        ans = {}
        if 'lb' in extraction:
            value, remaining = extraction.split('lb')
            ans[WEIGHT_UNIT_POUND] = int(value.strip())
        elif 'kg' in extraction:
            value, remaining = extraction.split('kg')
            ans[WEIGHT_UNIT_KILOGRAM] = int(value.strip())
        elif extraction.isdigit():
            if len(extraction) == 2:
                ans[WEIGHT_UNIT_KILOGRAM] = int(extraction)
            elif len(extraction) == 3:
                ans[WEIGHT_UNIT_POUND] = int(extraction)
            else:
                print 'WARNING: contain uncatched case:', extraction

        return ans

    ######################################################################
    #   Unit Transform
    ######################################################################
    @staticmethod
    def transform(extractions, target_unit):
        ans = []
        for extraction in extractions:
            imd_value = 0.
            for (unit, value) in extraction.iteritems():
                imd_value += WEIGHT_TRANSFORM_DICT[(unit, target_unit)] * value
            if WeightHelper.sanity_check(target_unit, imd_value):
                ans.append(imd_value)
        return ans

    ######################################################################
    #   Sanity Check
    ######################################################################
    @staticmethod
    def sanity_check(unit, value):
        if (unit, WEIGHT_UNIT_KILOGRAM) in WEIGHT_TRANSFORM_DICT:
            check_value = WEIGHT_TRANSFORM_DICT[
                (unit, WEIGHT_UNIT_KILOGRAM)] * value
            if check_value >= 30 and check_value <= 200:    # kg
                return True
        return False

    ######################################################################
    #   Output Format
    ######################################################################
    @staticmethod
    def format_output(value):
        return int(value)

    ######################################################################
    #   Main
    ######################################################################
    @staticmethod
    def extract_weight(text):
        return re_us_weight.findall(text) + re_ls_weight.findall(text)

    @staticmethod
    def extract(text):
        weight_extractions = WeightHelper.extract_weight(text)

        weight_extractions = WeightHelper.remove_dups(
            [WeightHelper.normalize_weight(_) for _ in weight_extractions])

        weight = {'raw': weight_extractions}

        for target_unit in [WEIGHT_UNIT_KILOGRAM, WEIGHT_UNIT_POUND]:
            weight[target_unit] = [WeightHelper.format_output(_) for _ in
                                   WeightHelper.transform(weight_extractions, target_unit)]
        output = {}

        if len(weight['raw']) > 0:
            output['weight'] = weight

        if 'weight' not in output:
            return None

        return output


if __name__ == '__main__':
    # text = """\n TS RUBI: THE NAME SAYS IT ALL!  \n INCALL $250 OUTCALL $350 \n \n \n \n \n \n Gender \n Age \n
    #            Ethnicity \n Hair Color \n Eye Color \n Height \n Weight \n Measurements \n Affiliation \n
    #            Availability \n Available To \n \n \n \n \n Transsexual \n 27 \n Latino/Hispanic \n Brown \n Hazel \n
    #            5'5\" \n 130 lb \n 34C - 28\" - 34\" \n """
    #
    # text = "\n \n Height: \r\n                        5'3''\r\n                      \n \n \n \n \n \n Weight: \r\n" \
    #        "                          125 lbs\r\n                       \n \n \n \n \n \n"
    #
    # text = "Breasts DD Eyes gray Height 1.52 Skin Tanned Weight 60"
    # text = "I am 25 of age, stand 5ft5in, fair in complexion, Long hair"
    #
    # text = "Measurements: 105lbs 5'2\" 34c with a beautiful face"
    #
    # text = "Travel: \n worldwide \n \n \n Weight: \n 117 lb (53 kg) \n \n \n " \
    #        "Height: \n 5.5 ft (166 cm) \n \n \n Ethnicity: \n Indian \n"
    #
    # text = "Hair Long Blonde Languages Afrikaans English Body Type slender Age 20-24 Breasts A " \
    #        "Eyes blue Height 1.78 Skin Fair Weight 51 Zandalee"

    text = "Hair Long Blonde Languages Afrikaans English Body Type slender Age 20-24 Breasts A Eyes " \
           "blue Height 1.78 Skin Fair Weight 51 Zandalee | Height 5'3\" Weight 103 | Invalid Height 220 Invalid " \
           "Weight 10kg"

    import json
    print json.dumps(WeightHelper.extract(text), indent=4)
