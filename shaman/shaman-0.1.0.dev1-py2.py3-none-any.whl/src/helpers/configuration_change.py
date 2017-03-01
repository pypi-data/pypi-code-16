from configparser import ConfigParser
from shaman.src.helpers.configuration_exceptions import (StagesBlockNotInConfiguration, StagesBlockIsEmptyInConfiguration,
                                      StageBlockIsMissing, MissingOrderParameterInStageBlock,
                                      NotUniqueOrderParameterInStageBlock)


class CustomParser(ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


def is_config_correct(initial_config):
    # checking if STAGES is not empty
    if "STAGES" in initial_config:
        if not initial_config["STAGES"]:
            raise StagesBlockIsEmptyInConfiguration()
    else:
        raise StagesBlockNotInConfiguration()


    # checking if a configuration block for a stage is missing
    stages_not_in_initial_config = []
    for stage in initial_config['STAGES']:
        if stage not in initial_config:
            stages_not_in_initial_config.append(stage)
    if stages_not_in_initial_config:
        raise StageBlockIsMissing(stages_not_in_initial_config)


    # checking if 'order' parameter is missing for any stage
    stages_with_missing_order = []
    for stage in initial_config['STAGES']:
        if 'order' not in initial_config[stage]:
            stages_with_missing_order.append(stage)
    if stages_with_missing_order:
        raise MissingOrderParameterInStageBlock(stages_with_missing_order)


    stages = list(initial_config['STAGES'].keys())
    print(stages)
    orders_dict = {i: initial_config[i]['order'] for i in stages}
    not_uniq_values = [x for n,x in enumerate(list(orders_dict.values())) if x in list(orders_dict.values())[:n]]
    if not_uniq_values:
        raise NotUniqueOrderParameterInStageBlock(not_uniq_values, orders_dict)

    return True

def ignore_fields(worker_config, field_list):
    worker_config = worker_config
    for field in field_list:
        if field in worker_config and field in worker_config['STAGES']:
            del worker_config[field]
            del worker_config['STAGES'][field]
        elif field in worker_config['STAGES']:
            del worker_config['STAGES'][field]
        elif field in worker_config:
            del worker_config[field]

    return worker_config


def ignore_after(worker_config, order):
    worker_config = worker_config
    fields_to_ignore = [field for field in worker_config
                              if 'order' in worker_config[field] and int(worker_config[field]['order']) > order]

    for field in fields_to_ignore:
        if field in worker_config and field in worker_config['STAGES']:
            del worker_config[field]
            del worker_config['STAGES'][field]
        elif field in worker_config['STAGES']:
            del worker_config['STAGES'][field]
        elif field in worker_config:
            del worker_config[field]

    return worker_config
