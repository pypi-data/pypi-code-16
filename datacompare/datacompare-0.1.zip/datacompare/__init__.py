__all__ = ['compare_datasets']

import pandas as pd
import numpy as np


SUFFIX_DF1 = '_df1'
SUFFIX_DF2 = '_df2'


def equals_condition(df1_columns_to_compare, df2_columns_to_compare):
    condition = []
    for col_x, col_y in zip(df1_columns_to_compare, df2_columns_to_compare):
        condition.append(col_x + ' == ' + col_y)
    return ' and '.join(condition)


def not_exists_condition(df_columns_to_compare):
    condition = []
    for col in df_columns_to_compare:
        condition.append(col)
    return ' + '.join(condition) + ' != ' + ' + '.join(condition)


def compare_datasets(df1, df2, df1_keys, df2_keys,
                     df1_columns_to_compare=None,
                     df2_columns_to_compare=None):

    if not df1_columns_to_compare:
        df1_columns_to_compare = list(column for column in df1.columns.difference(df1_keys))
    if not df2_columns_to_compare:
        df2_columns_to_compare = list(column for column in df2.columns.difference(df2_keys))

    for column in df1_columns_to_compare:
        if column in df2_columns_to_compare:
            df1_columns_to_compare[df1_columns_to_compare.index(column)] = column + SUFFIX_DF1
            df2_columns_to_compare[df2_columns_to_compare.index(column)] = column + SUFFIX_DF2

    df_result = pd.merge(df1, df2, how='outer', indicator=True,
                         suffixes=(SUFFIX_DF1, SUFFIX_DF2),
                         left_on=df1_keys, right_on=df2_keys)

    df_result.eval('equals = ' + equals_condition(df1_columns_to_compare,
                                                  df2_columns_to_compare),
                   inplace=True)
    df_result['_merge'] = np.where(df_result['equals'],
                                   'equals',
                                   df_result['_merge'])
    df_result.drop(labels='equals', axis=1, inplace=True)
    df_result.rename(columns={'_merge': 'result'}, inplace=True)
    return df_result
