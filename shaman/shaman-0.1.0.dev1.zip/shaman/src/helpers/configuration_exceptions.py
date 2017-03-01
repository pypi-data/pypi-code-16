class StagesBlockNotInConfiguration(Exception):
    def __init__(self):
        message = """

    ****
    STAGES block is missing in configuration. Please add some stages in configuration. No point to run shaman without any actions

    Configuration block [STAGES] contains a list of stages you want to run in the following formats (one of them is applicable):
        - <stage_name> = 'classname':<Name of classs in stage module> (ex. download_stage = 'classname':'DownloadStage') or
        - <stage_name> = 'classname':<Name of classs in stage module>,'python_class_filename':<name of module where class resides>

    The difference between them is if you want to use a stage twice in one project, you have to give them different names(<stage_name>).
    For instance:
    If you need to send result message to different mongo collections (or, even different mongo hosts), the example configuration may look like:
        - output_mongo_titles_stage = 'classname':'MongoOutputStage','python_class_filename':'mongo_output_stage'
        - output_mongo_extra_stage = 'classname':'MongoOutputStage','python_class_filename':'mongo_output_stage'
    ****
    """
        super(StagesBlockNotInConfiguration, self).__init__(message)


class StagesBlockIsEmptyInConfiguration(Exception):
    def __init__(self):
        message = """

    ****
    Empty STAGES block in configuration. Please add some stages in configuration. No point to run shaman without any actions

    Configuration block [STAGES] contains a list of stages you want to run in the following formats (one of them is applicable):
        - <stage_name> = 'classname':<Name of classs in stage module> (ex. download_stage = 'classname':'DownloadStage') or
        - <stage_name> = 'classname':<Name of classs in stage module>,'python_class_filename':<name of module where class resides>

    The difference between them is if you want to use a stage twice in one project, you have to give them different names(<stage_name>).
    For instance:
    If you need to send result message to different mongo collections (or, even different mongo hosts), the example configuration may look like:
        - output_mongo_titles_stage = 'classname':'MongoOutputStage','python_class_filename':'mongo_output_stage'
        - output_mongo_extra_stage = 'classname':'MongoOutputStage','python_class_filename':'mongo_output_stage'

    ****
    """
        super(StagesBlockIsEmptyInConfiguration, self).__init__(message)

class StageBlockIsMissing(Exception):
    def __init__(self, stages_not_in_initial_config):
        message = """

    ****
    Stage(s) {} in [STAGES] block does not have separated block for it.
    Please, add separated block for each stage according to stage docstring.
    ****
    """.format(",".join(stages_not_in_initial_config))
        super(StageBlockIsMissing, self).__init__(message)

class MissingOrderParameterInStageBlock(Exception):
    def __init__(self, stages_with_missing_order):
        message = """

    ****
    There is a mistake in your configuration file. Blocks ({}) did not have 'order' parameter.

    'order' is a required parameter for EVERY stage. Order is used by shaman to understand
    in what order to run stages.
    ****
    """.format(','.join(stages_with_missing_order))
        super(MissingOrderParameterInStageBlock, self).__init__(message)

class NotUniqueOrderParameterInStageBlock(Exception):
    def __init__(self, not_uniq_values, orders_dict):
        message = """

    ****
    Not unique 'order' parameter in following stages: """

        for order in not_uniq_values:
            d = {stage: value for stage, value in orders_dict.items() if value == order}
        message = message +"{}. " \
                                           "Invalid value: {}.".format(",".join(list(d.keys())), list(d.values())[0])
        super(NotUniqueOrderParameterInStageBlock, self).__init__(message+'\n    ****\n')