"""Compare instance reservations and running instances for AWS services."""

import click

from check_reserved_instances.calculate import (
    calculate_ec2_ris, calculate_elc_ris, calculate_rds_ris)
from check_reserved_instances.config import parse_config
from check_reserved_instances.report import report_results

current_config = {}


@click.command()
@click.option('--config', default='config.ini',
              help='Provide the path to the configuration file')
def cli(config):
    """Compare instance reservations and running instances for AWS services.

    Args:
        config (str): The path to the configuration file.
    """
    current_config = parse_config(config)

    results = {}

    aws_accounts = current_config['Accounts']

    for aws_account in aws_accounts:
        name = aws_account['name']
        results[name] = []
        results[name].append(calculate_ec2_ris(account=aws_account))

        if aws_account['rds'] is True:
            results[name].append(calculate_rds_ris(account=aws_account))
        if aws_account['elasticache'] is True:
            results[name].append(calculate_elc_ris(account=aws_account))

    report_results(current_config, results)
