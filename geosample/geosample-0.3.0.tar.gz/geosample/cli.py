# -*- coding: utf-8 -*-
import geojson
import click
import json
from .geosample import sample_geojson


@click.command()
@click.argument('geojson-file', type=click.File())
@click.option('-n', type=int, default=100, help='Total number of samples')
@click.option('-o', type=click.Path(exists=False),
              default='sample.geojson', help='Output path')
@click.option('-s', '--seed', type=int, default=1111,
              help='Random seed')
def main(geojson_file, n, o, seed):
    """Generate sample of locations in geojson polygons"""
    gj = json.loads(geojson_file.read())
    points = sample_geojson(gj, n, seed=seed)
    result = geojson.Feature(geometry=points, properties={})

    with open(o, 'w') as of:
        of.write(json.dumps(result))

