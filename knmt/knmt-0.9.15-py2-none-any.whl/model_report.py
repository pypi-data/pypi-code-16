import numpy as np
import bokeh.plotting
from bokeh.plotting import figure, output_file, show

from datetime import date
from random import randint

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, NumberFormatter
from bokeh.io import output_file, show, vform

from collections import namedtuple, defaultdict

import pandas as pd

from bokeh.charts import Donut

def commandline():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("model")
    parser.add_argument("dest")
    args = parser.parse_args()
    
    model = np.load(args.model)
    
    output_file(args.dest)
    
    
    Entry = namedtuple("Entry", "name full_size disk shape size_ratio min max mean std nb_tiny ratio_tiny amplitude smallest_non_zero nb_zeros ratio_zeros".split())

    sorted_keys = sorted(model.keys())
    total_size_params = sum(np.prod(model[key].shape) for key in model.keys())
    print total_size_params
    # datas = dict(name = [], shape = [], full_size = [], size_ratio = [], min = [], max = [], mean = [], std = [],
    #              amplitude = [], smallest_non_zero = [],
    #             nb_tiny = [], ratio_tiny = [], nb_zeros = [], ratio_zeros = [])
    datas = defaultdict(list)
    def add_entry(entry):
        entry_as_dict = entry._asdict()
        field_count = None
        for key in entry._fields:
            if field_count is None:
                field_count = len(datas[key])
            else:
                assert field_count == len(datas[key])
            datas[key].append(entry_as_dict[key])
    
    for key in sorted_keys:
        m = model[key]
        full_size = np.prod(m.shape)
        
        entry = Entry(
            name = key,
            full_size = full_size,
            disk = full_size * 4,
            shape = m.shape,
            size_ratio = full_size / float(total_size_params),
            min = np.min(m),
            max = np.max(m),
            mean = np.mean(m),
            std = np.std(m),
            nb_tiny = np.sum(np.abs(m) < 1e-5),
            ratio_tiny = np.sum(np.abs(m) < 1e-5)/float(full_size),
            amplitude = np.max(np.abs(m)),
            smallest_non_zero = np.min(np.abs(m)),
            nb_zeros = np.sum(m == 0),
            ratio_zeros = np.sum(m == 0)/float(full_size)
        )
        
        add_entry(entry)
                                  
#         print key, m.shape, full_size, full_size / float(total_size_params) * 100, "%"
#         print np.min(m), np.max(m), np.mean(m), np.std(m), np.sum(np.abs(m) < 1e-5), (np.sum(np.abs(m) < 1e-5)/float(full_size)) * 100, "%"
    # datas["name"].append("TOTAL")
    
        
    total_entry = Entry(
        name = "TOTAL",
        full_size = total_size_params,
        disk = total_size_params * 4,
        shape = (-1,-1),
        size_ratio = 1,
        min = min(datas["min"]),
        max = max(datas["max"]),
        mean = -1,
        std = -1,
        nb_tiny = sum(datas["nb_tiny"]),
        ratio_tiny = sum(datas["nb_tiny"]) / float(total_size_params),
        amplitude = max(datas["amplitude"]),
        smallest_non_zero = min(datas["smallest_non_zero"]),
        nb_zeros = sum(datas["nb_zeros"]),
        ratio_zeros = sum(datas["nb_zeros"]) / float(total_size_params)
    )
    
    add_entry(total_entry)
    
    
    def add_name_prefix(datas):
        max_nb_levels = 0
        for name in datas["name"]:
            splitted_name = name.split("/")
            max_nb_levels = max(max_nb_levels, len(splitted_name))
        for name in datas["name"]:
            splitted_name = name.split("/")
            for x in xrange(max_nb_levels):
                datas["prefix%i"%x].append(splitted_name[x] if x < len(splitted_name) else "_")
                
    add_name_prefix(datas)
    
    df = pd.DataFrame(datas)

    by_prefix = df[df["name"] != "TOTAL"][["prefix0", "prefix1", "full_size"]]#, "prefix2", "prefix3", "full_size"]]
    
    d = Donut(by_prefix, label=["prefix0", "prefix1"], values='full_size',
          text_font_size='8pt', hover_text='size')
    
    source = ColumnDataSource(datas)
    
    columns = [
        TableColumn(field="name", title="Name"),
        TableColumn(field="shape", title="shape"),
        TableColumn(field="full_size", title="full_size", formatter = NumberFormatter(format = "0,0")),
    TableColumn(field="disk", title="disk", formatter = NumberFormatter(format = "0.0b")),
        TableColumn(field="size_ratio", title="size_ratio", formatter = NumberFormatter(format = "0.00%")),
        TableColumn(field="min", title="min", formatter = NumberFormatter(format = "0.0000")),
        TableColumn(field="max", title="max", formatter = NumberFormatter(format = "0.0000")),
    TableColumn(field="mean", title="mean", formatter = NumberFormatter(format = "0.0000")),
    TableColumn(field="std", title="std", formatter = NumberFormatter(format = "0.0000")),
    TableColumn(field="nb_tiny", title="nb_tiny", formatter = NumberFormatter(format = "0,0")),
    TableColumn(field="ratio_tiny", title="ratio_tiny", formatter = NumberFormatter(format = "0.00%")),
    TableColumn(field="amplitude", title="amplitude", formatter = NumberFormatter(format = "0.0000")),
    TableColumn(field="smallest_non_zero", title="smallest_non_zero", formatter = NumberFormatter(format = "0.0[000000000]")),
    TableColumn(field="nb_zeros", title="nb_zeros", formatter = NumberFormatter(format = "0,0")),
    TableColumn(field="ratio_zeros", title="ratio_zeros", formatter = NumberFormatter(format = "0.00%"))
    ]

    data_table = DataTable(source=source, columns=columns,  height=650, fit_columns = True)
    
    show(vform(d, data_table))
    
if __name__ == '__main__':
    commandline()