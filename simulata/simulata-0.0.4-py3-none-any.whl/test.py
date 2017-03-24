import simulata

df = pd.DataFrame([[1, 10, 100, 1000], [2, 11, 112, 1113], [3,13,141,1451]], columns=list('ABCD'))
simulate_df(df, columns=['A'])
simulate_df(df)
simulate_df(df, exclude_columns=['A'])
