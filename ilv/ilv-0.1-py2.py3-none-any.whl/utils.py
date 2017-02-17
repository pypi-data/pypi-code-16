import pandas as pd

def list_of_dict_to_dict_of_list(list_of_dict):
    # http://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    dict_of_list = {}
    for d in list_of_dict:
        for k, v in d.items():
            if k not in dict_of_list:
                dict_of_list[k] = [v]
            else:
                dict_of_list[k].append(v)
    return dict_of_list


def filter_dict(d, keys):
    filtered = {}
    for k in keys:
        filtered[k] = d[k]
    return filtered


def moving_average_1d(list_, window):
    series = pd.Series(list_)
    return series.rolling(window=window, center=True).mean().tolist()
