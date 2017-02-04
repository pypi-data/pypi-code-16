import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import string
from descartes import PolygonPatch
from sklearn.externals import joblib
from matplotlib.collections import PatchCollection
from matplotlib import colors
import datetime as dt
import glob
import imageio
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def _get_list_of_dir_contents(path):
    pathz = glob.glob(os.path.join(path, '*'))
    return pathz


def _load_zip_geometry(shape_fn='ZIP_CODE_040114.shp'):
    try:
        path = os.path.join(_ROOT, 'data', 'zip_shapes.pkl')
        zip_geometry = joblib.load(path)#'data/zip_shapes.pkl')
    except:
        print('missing zip_shapes.pkl, please redownload package')
    return zip_geometry


def _get_plottable_zips(borough):
    zip_geometry = _load_zip_geometry()
    bnx_zips = [10453, 10457, 10460, 10458, 10467, 10468, 10451, 10452, 10456,
                10454, 10455, 10459, 10474, 10463, 10471, 10466, 10469, 10470,
                10475, 10461, 10462, 10464, 10465, 10472, 10473]

    bkn_zips = [11212, 11213, 11216, 11233, 11238, 11209, 11214, 11228, 11204,
                11218, 11219, 11230, 11234, 11236, 11239, 11223, 11224, 11229,
                11235, 11201, 11205, 11215, 11217, 11231, 11203, 11210, 11225,
                11226, 11207, 11208, 11211, 11222, 11220, 11232, 11206, 11221,
                11237]

    mhn_zips = [10026, 10027, 10030, 10037, 10039, 10001, 10011, 10018, 10019,
                10020, 10036, 10029, 10035, 10010, 10016, 10017, 10022, 10012,
                10013, 10014, 10004, 10005, 10006, 10007, 10038, 10280, 10002,
                10003, 10009, 10021, 10028, 10044, 10065, 10075, 10128, 10023,
                10024, 10025, 10031, 10032, 10033, 10034, 10040]

    qns_zips = [11361, 11362, 11363, 11364, 11354, 11355, 11356, 11357, 11358,
                11359, 11360, 11365, 11366, 11367, 11412, 11423, 11432, 11433,
                11434, 11435, 11436, 11101, 11102, 11103, 11104, 11105, 11106,
                11374, 11375, 11379, 11385, 11691, 11692, 11693, 11694, 11695,
                11697, 11004, 11005, 11411, 11413, 11422, 11426, 11427, 11428,
                11429, 11414, 11415, 11416, 11417, 11418, 11419, 11420, 11421,
                11368, 11369, 11370, 11372, 11373, 11377, 11378]

    sti_zips = [10302, 10303, 10310, 10306, 10307, 10308, 10309, 10312, 10301,
                10304, 10305, 10314]

    zip_dic = {'manhattan': mhn_zips, 'brooklyn': bkn_zips,
               'bronx': bnx_zips, 'queens': qns_zips,
               'richmond / staten island': sti_zips}
    borough_zips = zip_dic[borough]
    pzips = list(set(list(zip_geometry.index)) & set(borough_zips))
    return pzips


def _gif_naming_list(size):
    alphabet = list(string.ascii_lowercase)
    num_repeats = int(np.ceil(size / 26.0))
    gif_suffixes = []
    for a in alphabet:
        for a_rep in range(1, num_repeats + 1):
            gif_suffixes.append(a_rep * a)
    return gif_suffixes


def _generate_graphlabel(call_description):
    if call_description is None or call_description.lower() == 'all':
        graphlabel = 'All Calls'
    elif type(call_description) == list:
        graphlabel = 'Multi-Call Graph (#calls = ' + str(len(call_description)) + ')'
    else:
        if len(call_description) > 25:
            graphlabel = call_description[:25]
        else:
            graphlabel = call_description
    return graphlabel


def _clean_fn(fn):
    return fn.replace(':', '').replace('"', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('\/', '').replace('/', '').replace(' ', '_')


def _get_output_path(borough, freq, graphlabel):
    graph_folder = _clean_fn(graphlabel)
    output_path = borough + '/' + freq + '/' + graph_folder
    if not os.path.exists(output_path):
            os.makedirs(output_path)
    return output_path


def _generate_title(freq, time_period, graphlabel):
    if freq == 'hourly':
        if time_period > 9:
            time_string = 'Hour ' + str(time_period) + ':00'
        else:
            time_string = 'Hour 0' + str(time_period) + ':00'
    elif freq == 'weekly':
        time_string = 'Week ' + str(time_period)
    else:
        time_string = dt.datetime(2016, 1, 1) + dt.timedelta(int(time_period) - 1)
        time_string = time_string.strftime("%m/%d")
    return "Mean Count of " + graphlabel + " per year: " + time_string


def _plot_data(zip_counts, freq, graphlabel, output_path):
    zip_geometry = _load_zip_geometry()
    cm = plt.get_cmap('YlOrRd')
    gif_suffixes = _gif_naming_list(size=len(zip_counts.index))

    max_incident = np.nanmax(zip_counts.values.flatten())
    min_incident = np.nanmin(zip_counts.values.flatten())

    min_x, max_x = 2*10**8, -2*10**8
    min_y, max_y = 2*10**8, -2*10**8
    for i, time_period in enumerate(zip_counts.index):
        fig, ax = plt.subplots(figsize=(8, 8), dpi=500)
        counts = []
        geoms = []
        for zipcode in zip_counts.columns:
            count = zip_counts[zipcode].loc[time_period]
            zip_geom = zip_geometry.loc[zipcode][0]
            x, y = zip_geom.exterior.xy
            zip_x_min, zip_x_max = np.min(x), np.max(x)
            zip_y_min, zip_y_max = np.min(y), np.max(y)
            if zip_x_min < min_x:
                min_x = zip_x_min
            if zip_x_max > max_x:
                max_x = zip_x_max
            if zip_y_min < min_y:
                min_y = zip_y_min
            if zip_y_max > max_y:
                max_y = zip_y_max
            zip_geom = PolygonPatch(zip_geom)
            geoms.append(zip_geom)
            counts.append(count)

        cmap_norm = colors.Normalize(vmin=min_incident, vmax=max_incident)
        p = PatchCollection(geoms, cmap=cm, alpha=.8, norm=cmap_norm)
        p.set_array(np.array(counts))
        cax = ax.add_collection(p)
        ax.set_xlim([min_x*.999, max_x*1.001])
        ax.set_ylim([min_y*.999, max_y*1.001])
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.xaxis.set_ticks_position(position='none')
        ax.yaxis.set_ticks_position(position='none')
        ax.xaxis.set_ticklabels(ticklabels='')
        ax.yaxis.set_ticklabels(ticklabels='')
        cbar = fig.colorbar(cax, shrink=.7, norm=cmap_norm, ticks=[min_incident, max_incident])
        cbar.ax.set_yticklabels([str(min_incident), str(max_incident)[:5]])
        cbar.set_label('# ' + graphlabel + ' per year', fontsize=9, rotation=90)

        graph_title = _generate_title(freq, time_period, graphlabel)
        ax.set_title(graph_title, fontsize=13)
        fig.savefig(output_path + '/' + gif_suffixes[i] + '.png', filetype='png')
        plt.close(fig)


def make_gif(freq, borough='all', call_description=None, graphlabel=None,
             time_per_frame=.55, statenisland=False, graph=True):
    if graphlabel is None:
        graphlabel = _generate_graphlabel(call_description)
    output_path = _get_output_path(borough, freq, graphlabel)
    try:
        path = os.path.join(_ROOT, 'data', freq + '_data_dic.pkl')
        data_dic = joblib.load(path)
    except:
        print('freq must be set to either:\nhourly\nweekly')
        return
    if type(call_description) == list:
        multi_call_data = []
        for call_desc in call_description:
            multi_call_data.append(data_dic[call_desc])

        zip_counts = pd.concat(multi_call_data)
        zip_counts.reset_index(inplace=True)
        if freq == 'dayofyear':
            label = 'DAYOFYEAR'
        else:
            label = freq[:-2]
        zip_grouped = zip_counts.groupby('INCIDENT_' + label.upper())
        zip_counts = zip_grouped.sum()
    elif call_description is None or call_description.lower() == 'all':
        zip_counts = data_dic['all']
    else:
        zip_counts = data_dic[call_description]
    if graph:
        if not statenisland:
            sti_zips = _get_plottable_zips('richmond / staten island')
            zip_counts = zip_counts.drop(list(set(sti_zips) & set(zip_counts.columns)), axis=1)
        _plot_data(zip_counts, freq, graphlabel, output_path)
        images = []
        img_paths = sorted(_get_list_of_dir_contents(output_path))
        for filename in img_paths:
            images.append(imageio.imread(filename))
        imageio.mimsave(_clean_fn(graphlabel) + '.gif', images, duration=time_per_frame)
        exit
    else:
        return zip_counts
