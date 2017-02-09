# -*- coding: utf-8 -*-
import os
import pySMS.html.pathdata.prodChooser as stprodchooser
import pySMS.html.pathdata.stockTabTable as sttable
from pySMS.utils.excepetions import ProductChooserAddError, DataRetreivalError, InvalidItemError
from pySMS.data.export import Export

class Webpage:

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))

    class Logic:

        def __init__(self):
            self.exp = Export()
            self.item_library = self.exp.convert_to_dict(
                self.exp.unzip_from_gzip(
                    self.exp.data_files_list['ci_data_library.json.gz'])['content'].decode())

        @staticmethod
        def product_chooser_add_item(item_dict, table_dict):
            product = item_dict['prodNumber']
            description = item_dict['description']
            row_count = len(table_dict)
            match_count = 0
            match_dict = {}

            for k, v in table_dict.items():
                for _item in v:
                    if product == _item and description in v:
                        match_count += 1
                        match_dict[k] = {'product': product, 'description': description}
                    elif product == _item and 'None' in v:
                        match_count += 1
                        match_dict[k] = {'product': product, 'description': description}

            if match_count != 0:
                if match_count < 1:
                    return {'action': 'none', 'reason': 'no match found'}
                if match_count == 1:
                    for k, v in match_dict.items():
                        if int(str(k.strip('row'))) == 1:
                            return {'action': 'click', 'selector_count': 1, 'selectors': [stprodchooser.prodchooserAdd]}
                        elif int(str(k.strip('row'))) % 2 == 0:
                            if int(str(k.strip('row'))) == row_count:
                                return {'action': 'click', 'selector_count': 2, 'selectors': [
                                    stprodchooser.prodChooserAddLastFront + str(k.strip('row')) + stprodchooser.prodChooserAddLastBack,
                                    stprodchooser.prodChooserAddFront + str(k.strip('row')) + stprodchooser.prodChooserAddEvenBack]}
                            else:
                                return {'action': 'click', 'selector_count': 1, 'selectors': [
                                    stprodchooser.prodChooserAddFront + str(k.strip('row')) + stprodchooser.prodChooserAddEvenBack]}
                        elif int(str(k.strip('row'))) % 2 != 0:
                            return {'action': 'click', 'selector_count': 1, 'selectors': [
                                stprodchooser.prodChooserAddFront + str(k.strip('row')) + stprodchooser.prodChooserAddOddBack]}
            else:
                raise ProductChooserAddError(' product_chooser_add_item(item_dict, table_dict): No Match Found')

        @staticmethod
        def stock_tab_table_checkboxes(n):
            if int(n) == 1:
                return sttable.stTableCheckBoxInit
            elif int(n) % 2 == 0:  # is an even row
                return sttable.stTableCheckBoxRowEvenFront + n + sttable.stTableCheckBoxRowEvenBack
            else:  # is an odd row
                return sttable.stTableCheckBoxRowOddFront + n + sttable.stTableCheckBoxRowOddBack

        def get_item_info(self, item):
            for key, value in self.item_library.items():
                for book_key, book_value in value.items():
                    for product, page in book_value.items():
                        if product == item:
                            return page
                        else:
                            pass


        def bool_data_from_table(self, t_dict, data_list):
            item_id_dict = {}

            def format_bin_id(bin):
                if bin != "location_bin":
                    return bin
                else:
                    return ' '.join([bin.split("_")[0].title(), bin.split("_")[1].title()])


            item_info = self.get_item_info(t_dict['prodnumber'])


            if data_list[3] == "none":
                d_dict = {'case_number': str(data_list[0]).rstrip('.0'),
                          'lot_number': str(data_list[1]).rstrip('.0'),
                          'serial_number': str(data_list[2]).rstrip('.0')}

                if item_info == None:
                    return {'match_found': False, 'data': None}

                if item_info['data_parent'].split('_')[0] in ['kit', 'tray']:
                    if d_dict['serial_number'] != '' and d_dict['lot_number'] == '':
                        item_id_dict = {'type': 'serial', 'id': "Serial " + str(d_dict['serial_number']) + " ~ "}

                elif item_info['data_parent'].split('_')[0] in ['component', 'piece']:
                    if d_dict['serial_number'] == '' and d_dict['lot_number'] != '':
                        item_id_dict = {'type': 'lot', 'id': str(d_dict['lot_number'])}

                if item_id_dict['type'] == 'serial':
                    if item_id_dict['id'] in t_dict['lot_serial']:
                        return {'match_found': True, 'data': {'info': item_id_dict, 'row': t_dict['rowNumber'],
                                                              'checkbox_selector': self.stock_tab_table_checkboxes(
                                                                  t_dict['rowNumber']),
                                                              'case': t_dict['container']}}
                    if item_id_dict['id'] not in t_dict['lot_serial']:
                        return {'match_found': False, 'data': None}

                elif item_id_dict['type'] == 'lot':
                    if d_dict['case_number'] in t_dict['container']:
                        return {'match_found': True, 'data': {'info': item_id_dict, 'row': t_dict['rowNumber'],
                                                              'checkbox_selector': self.stock_tab_table_checkboxes(
                                                                  t_dict['rowNumber']),
                                                              'case': t_dict['container']}}
                    elif d_dict['case_number'] not in t_dict['container']:
                        return {'match_found': False, 'data': None}


            else:
                d_dict = {'case_number': str(data_list[0]).rstrip('.0'),
                          'lot_number': str(data_list[1]).rstrip('.0'),
                          'serial_number': str(data_list[2]).rstrip('.0'),
                          'bin': str(data_list[3])}

                if item_info['data_parent'].split('_')[0] in ['kit', 'tray']:
                    if d_dict['serial_number'] != '' and d_dict['lot_number'] == '':
                        item_id_dict = {'type': 'serial', 'id': "Serial " + str(d_dict['serial_number']) + " ~ ", 'bin': format_bin_id(d_dict['bin'])}

                elif item_info['data_parent'].split('_')[0] in ['component', 'piece']:
                    if d_dict['serial_number'] == '' and d_dict['lot_number'] != '':
                        item_id_dict = {'type': 'lot', 'id': str(d_dict['lot_number']), 'bin': format_bin_id(d_dict['bin'])}

                if item_id_dict['type'] == 'serial':
                    if item_id_dict['id'] in t_dict['lot_serial']:
                        if item_id_dict['bin'] in t_dict['container']:
                            return {'match_found': True, 'data': {'info': item_id_dict, 'row': t_dict['rowNumber'],
                                                                  'checkbox_selector': self.stock_tab_table_checkboxes(t_dict['rowNumber']),
                                                                  'case': t_dict['container']}}
                    if item_id_dict['id'] not in t_dict['lot_serial']:
                        return {'match_found': False, 'data': None}

                elif item_id_dict['type'] == 'lot':
                    if d_dict['lot_number'] in t_dict['lot_serial']:
                        if item_id_dict['bin'] in t_dict['container']:
                            return {'match_found': True, 'data': {'info': item_id_dict, 'row': t_dict['rowNumber'],
                                                                  'checkbox_selector': self.stock_tab_table_checkboxes(t_dict['rowNumber']),
                                                                  'case': t_dict['container']}}
                    elif d_dict['case_number'] not in t_dict['container']:
                        return {'match_found': False, 'data': None}
