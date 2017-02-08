import re
import requests

class FileUtils:
    raise_msg_header_not_found = 'HEADER_NOT_FOUND'

    @staticmethod
    def send_to_tltrepo(file_fullname, tltrepo_subdir):
        files = {'userfile': open(file_fullname, 'rb')}
        values = {'subdir': tltrepo_subdir, 'MAX_FILE_SIZE': '1024000'}
        response = requests.post("http://tltrepo.tp.cselt.it/upload.php", files=files, data=values)
        return response.status_code


    @staticmethod
    def strip_rows(command_output):
        multiline_str = ''
        for out_row in command_output.splitlines():
            multiline_str += out_row.rstrip() + '\n'
        return multiline_str;

    @staticmethod
    def remove_skip_rows(multiline_str, skip_str_array, skip_empty_lines):
        outr = ''
        for out_row in multiline_str.splitlines():
            found = 0
            for s in skip_str_array:
                if s in out_row:
                    found = 1
            if found == 0 and \
                    (not skip_empty_lines or (skip_empty_lines and out_row.rstrip() != "")):
                outr += out_row + '\n'
        return outr;

    @staticmethod
    def check_header_string_array(multiline_str, header_str_array):
        for out_row in multiline_str.splitlines():
            for idx, val in enumerate(header_str_array):
                if val[2] == 'REGEXP':
                    regexp = re.compile(val[1])
                    if regexp.search(out_row) is not None:
                        return True, val[0], out_row
                elif val[2] == 'STR':
                    if val[1] == out_row.rstrip():
                        return True, val[0], out_row
                else:
                    return False, "", ""
        return False, "", ""

    @staticmethod
    def remove_before_header_string(multiline_str, header_str):
        return multiline_str[multiline_str.find(header_str + '\n') + len(header_str + '\n'):]

    @staticmethod
    def remove_after_footer_string(multiline_str, footer_str):
        var = multiline_str[:multiline_str.find(footer_str)]
        return var.strip() + '\n'

    @staticmethod
    def extract_block(multiline_str, starting_row, ending_row, add_ending_row):
        copy = False
        outr = ''
        for line in multiline_str.splitlines():
            line = line.rstrip()
            if line == starting_row:
                copy = True
            elif copy == True and line == ending_row:
                if add_ending_row:
                    outr += line + '\n'
                copy = False
                break

            if copy:
                outr += line + '\n'
        return outr

    @staticmethod
    def add_char_to_every_row_if_not_exist(multiline_str, character):
        str2 = ''
        for out_row in multiline_str.splitlines():
            str2 += out_row + (character if character not in out_row else '') + '\n'
        return str2

    @staticmethod
    def parse_exact_table(multiline_str, header_column_position):
        result = []
        for out_result_row in multiline_str.splitlines():
            arr = []
            for i in range(0, len(header_column_position)):
                start_pos = header_column_position[i][0]
                if header_column_position[i][1] is None:
                    if i < len(header_column_position) - 1:
                        end_pos = header_column_position[i + 1][0] - 1
                    else:
                        end_pos = len(out_result_row)
                else:
                    end_pos = header_column_position[i][1] - 1
                d = out_result_row[start_pos:end_pos].strip()
                arr.append(d)

            # Si assicura che ci sia almeno una cella con un campo valorizzato
            if ''.join(str(elem) for elem in arr) != '':
                result.append(arr)

        return result

    @staticmethod
    def create_htmltable(command_output_array_table, first_row_html_header):
        """
           Add to output windows an HTML table with the command
        :param context:
        :param command_output:
        """
        str = '<table style="color:black" border="1" cellpadding="5">\n'
        str += '<thead>\n'
        if first_row_html_header:
            if len(command_output_array_table) > 0:
                for th in command_output_array_table[0]:
                    str += '<th>' + th + '</th>\n'
        str += '</thead>\n'

        str += '<tbody>\n'
        for idx, row in enumerate(command_output_array_table):
            if not first_row_html_header or idx > 0:
                str += '<tr>\n'

                for val in row:
                    str += '<td>' + val + '</td>\n'
                str += '</tr>\n'
        str += '</tbody>\n</table>\n'
        return str;
