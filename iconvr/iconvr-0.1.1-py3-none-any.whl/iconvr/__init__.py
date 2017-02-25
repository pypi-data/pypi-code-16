import argparse
import os
import io


def get_file_list(file_path: str) -> list:
    if not os.path.isdir(file_path):
        if os.path.isfile(file_path):
            return [file_path]
        return []

    file_list = []
    for root, _, files in os.walk(file_path):
        for file in files:
            abs_file = os.path.join(root, file)
            file_list.append(abs_file)
    return file_list


def get_options():
    parse = argparse.ArgumentParser(description="遍历当前文件并且转换文件编码")
    parse.add_argument('-f', '--src_encoding', default='gbk',
                       help='当前编码，默认gbk')
    parse.add_argument('-t', '--dst_encoding', default='utf8',
                       help='目标编码，默认utf8')
    parse.add_argument('-m', '--match', default=['.cpp', '.h'],
                       nargs='+', help='文件匹配规则，注意不能放到路径前，避免冲突')
    parse.add_argument('path', help='遍历的路径')
    return parse.parse_args()


def trans_encoding(abs_file: str, src_encoding: str,
                   dst_encoding: str) -> bool:
    fd = open(abs_file, 'r+', -1, src_encoding)
    try:
        txt = fd.read()
    except Exception:
        fd.close()
        return False
    else:
        fd.truncate(0)
        fd.close()

        with open(abs_file, 'w', -1, dst_encoding) as fd:
            fd.write(txt)
            return True
    return False


def main():
    options = get_options()
    abs_path = os.path.abspath(options.path)
    file_list = get_file_list(abs_path)

    for file in file_list:
        # 过滤
        if not os.path.splitext(file)[1] in options.match:
            continue
        if trans_encoding(file, options.src_encoding, options.dst_encoding):
            print(options.src_encoding, '=>', options.dst_encoding,
                  'succ', file)


main()
