import logging
from typing import List

import fiona
import numpy as np
import requests
from gbdx_auth import gbdx_auth
from shapely.geometry import Point, shape, Polygon
from gbdxtools import Interface
gbdx = Interface()

auth = gbdx_auth.get_session()
access_token = auth.access_token

log = logging.getLogger()

headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}


def fetch_point(x, y, idaho, folder_name='images/'):
    params = {"lat": y, "long": x, "width": 2048, "height": 2048, "token": access_token}
    idaho_url = "http://idaho.geobigdata.io/v1/chip/centroid/idaho-images/{image_id}".format(image_id=idaho['imageId'])
    r = requests.get(idaho_url, headers=headers, params=params)
    if not r.ok:
        log.error((r.status_code, x, y, idaho['imageId']))
    else:
        # if idaho['nativeTileFileFormat'] == 'TIF':
        #     filename = (idaho['imageId'] + "?lat=" + str(y) + "&long=" + str(x) + ".tif")
        # else:
        # complete_name = os.path.join(folder_name + filename)
        filename = (idaho['imageId'] + "?lat=" + str(y) + "&long=" + str(x) + ".png")
        if len(r.content) > 500000:
            if idaho['numBands']:
                with open(folder_name + idaho['numBands'] + "/" + filename, 'wb') as output_img:
                    output_img.write(r.content)
                    log.debug(x, y, idaho['imageId'], "written to file", filename)


def shp_to_polygons(shp_file="../China_Multipart.geojson/China_Multipart.shp") -> List[Polygon]:
    with fiona.collection(shp_file) as f:
        prov = shape([poly for poly in f][0].get('geometry'))  # Shapely object
    xmin, ymin, xmax, ymax = prov.bounds
    grid_list = []
    grid_height, grid_width = 1, 1
    x_val = np.arange(xmin, xmax, grid_width)
    y_val = np.arange(ymin, ymax, grid_height)
    for xv in x_val:
        for yv in y_val:
            poly = Polygon(
                [(xv, yv), (xv, yv + grid_height), (xv + grid_width, yv + grid_height), (xv + grid_width, yv)])
            if poly.intersects(prov):
                grid_list.append(poly)
    return grid_list, prov


def gb_fetch_images(results: List, xy):
    for p in results:
        for x_point, y_point in xy:
            fetch_point(x_point, y_point, p)

def filter_xy(tile: Polygon, prov: Polygon):
    x = np.linspace(tile.bounds[0], tile.bounds[2], num=10)
    y = np.linspace(tile.bounds[1], tile.bounds[3], num=10)
    xy = np.dstack(np.meshgrid(x, y)).reshape(-1, 2)
    return [(x_point, y_point) for x_point, y_point in xy if prov.contains(Point(x_point, y_point))]

def main():
    polygons, prov = shp_to_polygons()
    for tile in polygons:

        results = gbdx.catalog.search(searchAreaWkt=tile.wkt, types=["IDAHOImage"])
        for p in results:
            for x_point, y_point in filter_xy(tile, prov):
                fetch_point(x_point, y_point, p)

if __name__ == '__main__':
    main()
