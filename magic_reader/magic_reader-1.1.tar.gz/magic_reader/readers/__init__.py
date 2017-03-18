import re


def parse_source_path(source_path):
    values = re.findall(r'\(([^()]+)\)', source_path)
    keys = [c for c in re.sub(r"\([^)]*\)", " ", source_path).split(' ') if c]
    return {key: value for key, value in zip(keys, values)}
