import pandas as pd

def get_header(line):
    return line.split()

def get_data(line):
    return line.split()[1:]
    
def get_data_dict(stats_path, logger):
    data_dict = dict()
    read_header = False

    line_counter = 1
    with open(stats_path, 'r') as f_open:
        for line in f_open:
            if line_counter == 1:
                header = get_header(line)
                line_counter += 1
            else:
                data = get_data(line)
                for i, j in enumerate(header):
                    if j == 'Reads':
                        data_dict[j] = int(data[i])
                    elif j == 'Objective':
                        data_dict[j] = float(data[i])
                    else:
                        data_dict[j] = data[i]
                line_counter += 1
    return data_dict

def run(gdc_uuid, stats_path, run_uuid, engine, logger):
    data_dict = get_data_dict(stats_path, logger)
    data_dict['gdc_uuid'] = gdc_uuid
    data_dict['run_uuid'] = [run_uuid]
    df = pd.DataFrame(data_dict)
    table_name = 'optityper_result'
    df.to_sql(table_name, engine, if_exists='append')
    return
