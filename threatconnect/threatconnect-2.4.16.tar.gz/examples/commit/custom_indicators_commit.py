""" standard """
import ConfigParser
import sys
from collections import OrderedDict
from random import randint

""" custom """
from threatconnect import ThreatConnect
from threatconnect.Config.IndicatorType import IndicatorType

# configuration file
config_file = "tc.conf"

# retrieve configuration file
config = ConfigParser.RawConfigParser()
config.read(config_file)

try:
    api_access_id = config.get('threatconnect', 'api_access_id')
    api_secret_key = config.get('threatconnect', 'api_secret_key')
    api_default_org = config.get('threatconnect', 'api_default_org')
    api_base_url = config.get('threatconnect', 'api_base_url')
    api_result_limit = int(config.get('threatconnect', 'api_result_limit'))
except ConfigParser.NoOptionError:
    print('Could not retrieve configuration file.')
    sys.exit(1)

tc = ThreatConnect(api_access_id, api_secret_key, api_default_org, api_base_url)
tc.set_api_result_limit(api_result_limit)
tc.report_enable()

owner = 'System'  # org or community
rn = randint(1, 100)  # random number generator for testing

def main():
    """ """
    # set threat connect log (tcl) level
    tc.set_tcl_file('log/tc.log', 'debug')
    tc.set_tcl_console_level('critical')
    tc.report_enable()

    # # (Required) Instantiate a Resource Object
    resources = tc.indicators()

    try:
        resources.retrieve()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    print "# of indicators retrieved: {}".format(len(resources))

    fruit = OrderedDict()
    fruit['size'] = 'large'
    fruit['shape'] = 'triangluar'
    resource = resources.add(fruit, owner=owner, type=IndicatorType.CUSTOM_INDICATORS, api_entity='fruit')

    known_resource = resources.add('0.1.1.0', owner=owner, type=IndicatorType.ADDRESSES)

    fruit_without_order = dict()
    fruit_without_order['size'] = 'petite'
    fruit_without_order['shape'] = 'rotund'
    resource_without_order = resources.add(fruit_without_order, owner=owner, type=IndicatorType.CUSTOM_INDICATORS, api_entity='fruit')

    try:
        print('Adding known resources {0!s}.'.format(known_resource.indicator))
        known_resource.commit()
        print('Adding resource {0!s}.'.format(resource.indicator))
        resource.commit()
        print('Adding resource without order {0!s}.'.format(resource_without_order.indicator))
        resource_without_order.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    resource.set_confidence(rn)
    resource.set_rating(randint(1, 5))

    try:
        print('Updating resource {0!s}.'.format(resource.indicator))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    try:
        print('Deleting resource {0!s}.'.format(resource.indicator))
        resource.delete()
        print('Deleting known_resource {0!s}.'.format(resource.indicator))
        known_resource.delete()
        print('Deleting resource_without_order {0!s}.'.format(resource.indicator))
        resource_without_order.delete()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)


    # # inc_resources = tc.incidents()
    # # inc_resource = inc_resources.add('TEST_INDCIDENT', owner=owner)
    # # inc_resource.set_name('LU Incident #{0:d}'.format(randint(1, 30)))
    # #
    # # # additional properties can be updated
    # # inc_resource.set_event_date('2015-03-{0:d}T00:00:00Z'.format(randint(1, 30)))
    # #
    # # inc_resource.commit()
    # #
    # #
    # # ind_resources = tc.indicators()
    # # fruit = OrderedDict()
    # # fruit['size'] = 'baby'
    # # fruit['shape'] = 'cakes'
    # # ind_resource = ind_resources.add(fruit, owner='OpenSource', type=IndicatorType.CUSTOM_INDICATORS, api_entity='fruit')
    # # ind_resource.commit()
    # #
    # ind_resources = tc.indicators()
    #
    # filter = ind_resources.add_filter(IndicatorType.CUSTOM_INDICATORS, api_entity='fruit')
    # # filter = ind_resources.add_filter(IndicatorType.ADDRESSES)
    # # filter.add_filter_operator(FilterSetOperator.OR)
    # filter.add_owner('OpenSource')
    #
    # ind_resources.retrieve()
    # inc_resources = tc.incidents().retrieve()
    #
    # # ind_resources.retrieve()
    # # addr = ind_resources.add('1.2.3.1', owner=owner, type=IndicatorType.ADDRESSES)
    # # addr.commit()
    # # print "{0!s} indicators found".format(len(ind_resources))
    # # for x in inc_resources:
    # #     x.associate_indicator(IndicatorType.ADDRESSES, addr.indicator)
    # #     x.commit()
    # #
    # # for x in inc_resources.retrieve():
    # #     print "{} : {}".format(x, x.indicator_associations)
    # for j in ind_resources:
    #     for i in inc_resources:
    #         i.associate_custom_indicator(j, api_entity='fruit')
    #         i.commit()
    #
    # # for i in tc.incidents().retrieve():
    # #     # print "Incident: {}".format(i.id)
    # #     for assoc in i.indicator_custom_associations('fruit'):
    # #         print "Association: {}".format(assoc.indicator)
    #
    #
    #
    # # ind_resource.associate_group()


if __name__ == "__main__":
    main()
    sys.exit()