import click
from geo import LocationDataSet


@click.command()
@click.argument('input_file', type=click.File('rb'), required=True)
@click.argument('output_file', type=click.File('wb'), required=True)
@click.option('--driving', is_flag=True)
def main(input_file, output_file, driving):
    """Geographic Midpoint Ranker"""
    location_data = LocationDataSet(input_file)
    location_data.build_report(is_driving=driving)
    location_data.save(output_file)
