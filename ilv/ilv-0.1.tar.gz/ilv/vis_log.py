import bokeh.charts
import bokeh.models.layouts
import numpy as np

from ilv.utils import filter_dict, list_of_dict_to_dict_of_list, moving_average_1d


np.random.seed(1)


def find_valid_keys(args_list, black_list=['outdir', 'gpu']):
    keys = args_list[0].keys()
    valid_keys = []
    for key in keys:
        if key not in black_list:
            cur = None
            for args in args_list:
                if cur is None:
                    cur = args[key]
                if cur != args[key]:
                    valid_keys.append(key)
                    break
    return valid_keys


def find_labels(args_list, valid_keys):
    """
    Args:
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.

    Returns:
        labels (list of strings)
    """
    # ignore keys which have no variation among results
    labels = []
    for args in args_list:
        label = ''
        for key in valid_keys:
            label += '{}={},'.format(key, args[key])
        labels.append(label)
    return labels


# this code is based on bokeh/examples/app/line_on_off.py
def vis_log(dfs, xs, ys, table_ys, args_list):
    """Merge all results on values ys

    Args:
        dfs (list of pd.DataFrame)
        args_list (list of dictionary): dictionary consists of keys and values
            that uniquely identify the plot.
        ys (list of strings)
        table_ys (dictionary of strings): key is name of y to display on
            dictionary. The value is how to turn the vector value into
            scalar ({'min', 'max'}).
        xs (list of strings)
    """
    # prepare and preprocess dataframes
    dict_args = list_of_dict_to_dict_of_list(args_list)
    valid_keys = find_valid_keys(args_list)
    dict_args = filter_dict(dict_args, valid_keys)
    labels = find_labels(args_list, valid_keys)

    # add hover functionality
    hover = bokeh.models.HoverTool(
            tooltips=[
                ("y", "$y"),
                ("label", "@legend"),
            ])
    p = bokeh.plotting.figure(tools=[hover], plot_width=1200, plot_height=825)

    # ys_dict == {string (y): List(Serial Data)}
    table_ys_dict = {}
    xs_dict = {}
    ys_dict = {}
    descs = []
    for x in xs:
        xs_dict[x] = []
    for y in ys:
        ys_dict[y] = []
    for table_y in table_ys.keys():
        table_ys_dict[table_y] = []
    for i, (args, label) in enumerate(zip(args_list, labels)):
        # get df from a result
        tmp = dfs
        for key, val in args.items():
            tmp = tmp[tmp[key] == val]
        for x in xs:
            xs_dict[x].append(tmp[x].values.tolist())
        for y in ys:
            ys_dict[y].append(tmp[y].values.tolist())
        descs.append([label] * len(tmp))
        for table_y, value_type in table_ys.items():
            if value_type == 'min':
                table_ys_dict[table_y].append(tmp[table_y].min())
            elif value_type == 'max':
                table_ys_dict[table_y].append(tmp[table_y].max())
            else:
                raise ValueError

    # build empty multi line graph
    multi_l_source = bokeh.plotting.ColumnDataSource(
        {'xs': [], 'ys': [], 'descs': [], 'legend': []})
    multi_l = p.multi_line(
        xs='xs', ys='ys', source=multi_l_source, legend='legend')

    # build datatable
    # build columns
    columns = []
    for key in valid_keys + table_ys.keys():
        columns.append(
            bokeh.models.widgets.TableColumn(field=key, title=key))
    # build data for the table
    data = {}
    # experiment configs
    for args in args_list:
        for key in valid_keys:
            if key not in data:
                data[key] = []
            data[key].append(args[key])
    # table y
    for table_y in table_ys.keys():
        data[table_y] = table_ys_dict[table_y]
    data['index'] = range(len(args_list))
    data_table_source = bokeh.models.ColumnDataSource(data)
    data_table = bokeh.models.widgets.DataTable(
        source=data_table_source, columns=columns,
        width=600, height=825)

    # NOTE: callback_policy, callback_throttle are not supported for
    # callbacks written in Python.
    window_slider = bokeh.models.Slider(
        start=1, end=101, value=1, step=10,
        title='window size')

    xs_button = bokeh.models.widgets.RadioButtonGroup(
        labels=xs, active=0, width=600)
    ys_button = bokeh.models.widgets.RadioButtonGroup(
        labels=ys, active=0, width=600)
    menu = ['top_right', 'top_left', 'bottom_right', 'bottom_left']
    legend_button = bokeh.models.widgets.RadioButtonGroup(
        labels=menu, active=0, width=600)

    colors_10_ids = np.random.permutation(10)
    colors_255_ids = np.random.permutation(255)

    def update(attr, old, new):
        raw_indices = data_table_source.selected['1d']['indices']

        # after sorting, the order of index changes
        reordered_keys = data_table_source.data['index']
        selected_indices = []
        for idx in raw_indices:
            selected_indices.append(reordered_keys[idx])

        # get list of selected line data
        selected_xs = []
        selected_ys = []
        selected_descs = []
        selected_labels = []
        for idx in selected_indices:
            selected_descs.append(descs[idx])
            selected_labels.append(labels[idx])
            x = xs[xs_button.active]
            y = ys[ys_button.active]
            selected_xs.append(xs_dict[x][idx])
            selected_ys.append(
                moving_average_1d(ys_dict[y][idx], window_slider.value))

        # get colors
        selected_colors = []
        if len(selected_indices) < 10:
            colors = bokeh.palettes.Category10_10
            ids = colors_10_ids
        else:
            colors = bokeh.palettes.Inferno256
            ids = colors_255_ids
        for i in range(len(selected_indices)):
            selected_colors.append(colors[ids[i]])

        # set data dict
        data = dict(xs=selected_xs, ys=selected_ys,
                    descs=selected_descs,
                    line_color=selected_colors,
                    legend=selected_labels)
        multi_l.data_source.data = data
        # set color
        # https://groups.google.com/a/continuum.io/forum/#!topic/bokeh/MMxjMK84n5M
        multi_l.glyph.line_color = 'line_color'

        p.legend.location = menu[legend_button.active]

    data_table_source.on_change('selected', update)
    window_slider.on_change('value', update)
    ys_button.on_change('active', update)
    xs_button.on_change('active', update)
    legend_button.on_change('active', update)

    # add tools
    p.add_tools(bokeh.models.BoxZoomTool())
    p.add_tools(bokeh.models.ResizeTool())
    p.add_tools(bokeh.models.SaveTool())
    p.add_tools(bokeh.models.WheelZoomTool())
    p.add_tools(bokeh.models.RedoTool())
    p.add_tools(bokeh.models.ResetTool())
    p.add_tools(bokeh.models.UndoTool())
    p.add_tools(bokeh.models.ZoomOutTool())
    p.add_tools(bokeh.models.ZoomInTool())

    # build layout
    sliders = bokeh.layouts.widgetbox(window_slider)
    xs_ys_widgets = bokeh.layouts.widgetbox(
        xs_button, ys_button)
    legend_widget = bokeh.layouts.widgetbox(legend_button)
    layout = bokeh.layouts.gridplot(
        [[data_table, p],
         [sliders, xs_ys_widgets, legend_widget]], sizing_mode='fixed')
    bokeh.io.curdoc().add_root(layout)
