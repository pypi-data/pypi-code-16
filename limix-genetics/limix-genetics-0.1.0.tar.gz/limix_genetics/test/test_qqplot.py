# from __future__ import division
#
# from time import time
#
# import pandas as pd
# from numpy import arange
# from numpy.random import RandomState
#
# from limix_genetics import qqplot
#
#
# def _create_df(label, pvals, marker):
#     df_ = pd.DataFrame(columns=['label', 'marker', 'p-value'])
#     df_['p-value'] = df_['p-value'].astype(float)
#     df_['p-value'] = pvals
#     df_['label'] = label
#     df_['marker'] = marker
#     df_.set_index(['label', 'marker'], inplace=True)
#     return df_


# def test_qqplot():
#     random = RandomState(0)
#     n = 10000000
#     pvals0 = random.rand(n)
#     pvals1 = random.rand(n)
#     marker = arange(n)
#
#     df = pd.DataFrame(columns=['label', 'marker', 'p-value']).set_index(
#         ['label', 'marker'])
#     df['p-value'] = df['p-value'].astype(float)
#
#     df = df.append(_create_df('qep', pvals0, marker))
#     df = df.append(_create_df('lmm', pvals1, marker))
#
#     df.sort_index(inplace=True)
#
#     start = time()
#     qqplot(df)
#
#
# if __name__ == '__main__':
#     test_qqplot()
