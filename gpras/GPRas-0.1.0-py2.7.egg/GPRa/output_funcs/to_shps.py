# -*- coding: utf-8 -*-

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString


def to_shps(oo, filename_prefix=None, crs=None, items=[]):
    if filename_prefix is None:
        filename_prefix = "temp_output/temp_shp"
    dirname = os.path.dirname(filename_prefix)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    filename1 = filename_prefix+'_nodes.shp'
    filename2 = filename_prefix+'_links.shp'

    node_geom = []
    node_df = oo.get_nodedf(items)
    for i in range(len(node_df)):
        this_row = node_df.iloc[i]
        xx = this_row['xcor']
        yy = this_row['ycor']
        pt = Point(xx,yy)
        node_geom.append(pt)
    node_gdf = gpd.GeoDataFrame(node_df, crs=crs, geometry=node_geom)

    nodes = oo.nodes
    links = oo.mainobj.link
    link_dic = {}
    link_geom = []
    i = 0
    for alink in links:
        oo = alink[0]
        dd = alink[1]
        x0,y0 = nodes[oo]
        x1,y1 = nodes[dd]
        line = LineString(((x0,y0),(x1,y1)))
        link_geom.append(line)
        link_dic[i] = {'origin_id':oo, 'destination_id':dd, 'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1}
        i+=1
    link_df = pd.DataFrame.from_dict(link_dic, orient='index')
    link_gdf = gpd.GeoDataFrame(link_df, crs=crs, geometry=link_geom)

    node_gdf.to_file(filename=filename1, driver='ESRI Shapefile')
    link_gdf.to_file(filename=filename2, driver='ESRI Shapefile')
