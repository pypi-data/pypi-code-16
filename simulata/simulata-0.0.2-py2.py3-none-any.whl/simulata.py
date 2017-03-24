simulata_version = "0.0.2"

def simulate_df(input_df, output_rows = 100, columns=True, exclude_columns=None):
    value_dict = {}
    if columns is True:
        columns_simulate = input_df.columns
    else:
        columns_simulate = []
        columns_simulate = columns_simulate.append(columns)

    if exclude_columns is not None:
        columns_simulate = input_df.columns
        if type(exclude_columns) is list:
            for column_drop in exclude_columns:
                input_df = input_df.drop(column_drop, axis=1)
        else:
            input_df = input_df.drop(exclude_columns, axis=1)
        columns_simulate = input_df.columns
        #print("columns_simulate: ", columns_simulate)

    output_df = pd.DataFrame(columns=columns_simulate)

    for column_name in columns_simulate:
        value_dict[column_name] = df[column_name].unique()


    for count in range(0,output_rows):
        row = {}
        for column_name in columns_simulate:
            row[column_name] = np.random.choice(value_dict[column_name])
        output_df = output_df.append(row, ignore_index=True)

    return output_df
