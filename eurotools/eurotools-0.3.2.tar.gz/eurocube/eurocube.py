import six
import unicodedata
from . import cube_utils


def getCube(cube_info, redis):
    """
        This function return a connection with an olap cube.
        **Args:**
            cube_info: A dict with cube_ip (string), cube_db (string), cubes (list of strings), limit_sim_exe and limit_time keys.
            redis: An instance of redis object.
        **Returns:**
            Return am object wich is a connection with an olap cube

        **Extra info:**
            To see more info go to :class: cube_utils.Cube
    """
    cube = cube_utils.Cube(limit_sim_exe=cube_info['limit_sim_exe'], limit_time=cube_info['limit_time'])
    cube.connect(cube_info['cube_ip'], cube_info['cube_db'], cube_info['cubes'], redis)
    return cube


def getCubeInfo(cube, request_data, dimension_indicators, cf, filters=False, dim_date=('Date', 'Date', 'Date')):
    measures_indicators = cf.med_cube_prec
    name_cube = cf.cube_name
    mdx_class = cube_utils.Mdx(dim_date=dim_date, format_date_in=cf.format_date, format_date_out=cf.format_date, only_date=True)
    where = getWhere(request_data, cf, dim_date, cf.format_date, filters, dimension_indicators)
    mdx = mdx_class.mdx(cube, part_rows=dimension_indicators, part_columns=measures_indicators, part_from=name_cube, part_where=where)
    res = cube.launch_query(mdx)
    return res


def getWhere(request_data, cf, dim_date, format_date, filters, dimension_indicators=[]):
    where = {}
    if 'from_date' in request_data and 'to_date' in request_data:
        where = {dim_date: (request_data['from_date'].strftime(format_date), request_data['to_date'].strftime(format_date))}

    for col in cf.col_cube_complete_map_keys:
        if col in request_data and request_data[col] != 'NULL':
            dim = cf.attr_to_filter.get(col, cf.col_cube_complete_map[col])
            if not filters or dim not in dimension_indicators:
                before = []
                if dim in where:
                    before = where[dim]
                where[dim] = before + request_data[col].split(',')
    return where


def getDimensionSelected(groupby, col_cube_complete_map):
    dimensions = {}
    for dim in groupby:
        if dim in col_cube_complete_map:
            dimensions[col_cube_complete_map[dim]] = dim
    return dimensions


def getMeasureSelected(list_neasures, measure_complete_map):
    measures = {}
    for mea in list_neasures:
        if mea in measure_complete_map:
            measures[measure_complete_map[mea]] = mea
    return measures


def getFormatFilter(cube, res, dim_selected, dim_to_filter=None):
    dimension_str = '.'.join('[{0}]'.format(el) for el in dim_selected)
    if dim_to_filter:
        dim_to_filter_str = '.'.join('[{0}]'.format(el) for el in dim_to_filter)
    else:
        dim_to_filter_str = dimension_str
    json_data = getDictFormat(cube, res)
    data = []
    for row in json_data:
        data.append({'id': row[dim_to_filter_str], 'text': row[dimension_str]})
    return data


def getFormatGrid(cube, res, dimension_indicators, measures):
    dimensions_str = dict(('.'.join('[{0}]'.format(el) for el in dim_selected), dimension_indicators[dim_selected]) for dim_selected in dimension_indicators)
    measures_str = [mea_selected[1] for mea_selected in measures]
    json_data = getDictFormat(cube, res)
    data = []
    for row in json_data:
        row_aux = {}
        for dim in dimensions_str:
            if dim in row:
                row_aux[dimensions_str[dim]] = removeSpecialChar(row[dim])
            else:
                row_aux[dimensions_str[dim]] = ' -- '
        for meas in measures_str:
            row_aux[meas] = row[meas]
        data.append(row_aux)
    return data


def getFormatPie(cube, res, dimension_indicators, measures):
    dimensions_str = dict(('.'.join('[{0}]'.format(el) for el in dim_selected), dimension_indicators[dim_selected]) for dim_selected in dimension_indicators)
    measures_str = [mea_selected[1] for mea_selected in measures]
    json_data = getDictFormat(cube, res)
    data = []
    for row in json_data:
        row_aux = {}
        for dim in dimensions_str:
            if dim in row:
                row_aux['name'] = removeSpecialChar(row[dim])
        for meas in measures_str:
            row_aux['y'] = row[meas]
        data.append(row_aux)
    return data


def getDictFormat(cube, res):
    format = cube_utils.Format()
    json_data = format.dict(cube, res, complete_name=False)
    return json_data


def getSeries(cube, dims_group_by_highcharts, dimension_indicators, cf, request_data):
    dimension_indicators.append(dims_group_by_highcharts)
    dict_higcharts = getCubeInfo(cube, request_data, dimension_indicators, cf)
    dict_higcharts = getDictFormat(cube, dict_higcharts)
    return dict_higcharts


def getFormatMap(cube, data, dimension_indicators, measure, mapeo_provincias):
    dimensions_str = ['.'.join('[{0}]'.format(el1) for el1 in el) for el in dimension_indicators][0]
    json_data = getDictFormat(cube, data)
    result = []
    for row in json_data:
        new_row = {}
        provincia = removeSpecialChar(row[dimensions_str])
        if provincia in mapeo_provincias:
            cod_prov = 'es-' + mapeo_provincias[provincia].lower()
            new_row['hc-key'] = cod_prov
            new_row['value'] = row[measure]
            result.append(new_row)
    return result


def removeSpecialChar(value):
    if six.PY3:
        if isinstance(value, str):
            return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8')
    return value


def testConnection(cube_info, redis):
    try:
        cube = getCube(cube_info, redis)
        catalogs = cube.connection.getCatalogs()
    except:
        return False, 'CUBE IP ({0}) is wrong or the sql server not respond'.format(cube_info['cube_ip'])
    if not catalogs:
        return False, 'Not exists catalogs in CUBE IP ({0}), is wrong or the sql server not respond'.format(cube_info['cube_ip'])
    else:
        catalogs_names = [catalog.getUniqueName() for catalog in catalogs]
        if cube_info['cube_db'] not in catalogs_names:
            return False, 'CUBE DB ({0}) is not visible or not exists in the sql server'.format(cube_info['cube_db'])
        else:
            for catalog in catalogs:
                if catalog.getUniqueName() == cube_info['cube_db']:
                    cubes = catalog.getCubes()
            cubes_names = [cube_object.getUniqueName() for cube_object in cubes]
            all_cubes = True
            not_in = []
            for cube_config in cube_info['cubes']:
                if cube_config not in cubes_names:
                    all_cubes = False
                    not_in.append(cube_config)
            message = ''
            if not all_cubes:
                message = 'The cubes {0} not exists in sql server'.format(not_in)
            return all_cubes, message


def launchMdx(cube_info, redis, mdx):
    cube = getCube(cube_info, redis)
    res = cube.launch_query(mdx)
    json_data = getDictFormat(cube, res)
    return json_data
