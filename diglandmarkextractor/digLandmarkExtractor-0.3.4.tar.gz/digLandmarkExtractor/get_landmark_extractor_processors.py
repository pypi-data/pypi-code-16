from digExtractor.extractor_processor import ExtractorProcessor
from digLandmarkExtractor.dig_landmark_extractor import DigLandmarkExtractor
from digLandmarkExtractor.dig_multiplexing_landmark_extractor import DigMultiplexingLandmarkExtractor


def get_multiplexing_landmark_extractor_processor(rule_sets,
                                                  input_fields,
                                                  selector_function,
                                                  output_fields=None,
                                                  include_context=False,
                                                  minimum_pct_rules=0.5,
                                                  metadata=None):
    generate_output_fields = output_fields is None
    if generate_output_fields:
        output_fields = set()

    extractors = dict()
    for key, rule_set in rule_sets.iteritems():
        extractor = DigLandmarkExtractor()
        extractor.set_rule_set(rule_set)
        if metadata:
            extractor.set_metadata(metadata)
        else:
            extractor.set_metadata({"extractor": "landmark"})
        extractor.set_minimum_pct_rules(minimum_pct_rules)
        extractors[key] = extractor
        extractor.set_include_context(include_context)
        if generate_output_fields:
            output_fields.update(extractor.get_trimmed_rule_names())

    extractor = DigMultiplexingLandmarkExtractor()
    extractor.set_extractors(extractors)
    extractor.set_selector_function(selector_function)
    extractor.set_metadata({"extractor": "landmark"})
    extractor.set_include_context(include_context)
    extractor_processor = ExtractorProcessor()\
        .set_extractor(extractor)\
        .set_input_fields(input_fields)\
        .set_output_fields(list(output_fields))
    return extractor_processor


def get_landmark_extractor_processor_for_rule_set(rule_set,
                                                  input_fields,
                                                  output_fields=None,
                                                  include_context=False,
                                                  minimum_pct_rules=0.5,
                                                  metadata=None):
    extractor = DigLandmarkExtractor()
    extractor.set_rule_set(rule_set)
    if metadata:
        extractor.set_metadata(metadata)
    else:
        extractor.set_metadata({"extractor": "landmark"})
    extractor.set_include_context(include_context)
    extractor.set_minimum_pct_rules(minimum_pct_rules)
    if output_fields is None:
        output_fields = extractor.get_trimmed_rule_names()
    extractor_processor = ExtractorProcessor()\
        .set_extractor(extractor)\
        .set_input_fields(input_fields)\
        .set_output_fields(output_fields)
    return extractor_processor


def get_landmark_extractor_processors(rule_set, input_fields,
                                      include_context=False,
                                      minimum_pct_rules=0.5,
                                      metadata=None):
    extractor_processors = list()
    for rule in rule_set.rules:
        extractor = DigLandmarkExtractor()
        extractor.set_rule(rule)
        if metadata:
            extractor.set_metadata(metadata)
        else:
            extractor.set_metadata({"extractor": "landmark"})
        extractor.set_include_context(include_context)
        extractor.set_minimum_pct_rules(minimum_pct_rules)
        output_field = extractor.get_trimmed_rule_names()
        extractor_processor = ExtractorProcessor()\
            .set_extractor(extractor)\
            .set_input_fields(input_fields)\
            .set_output_field(output_field)
        extractor_processors.append(extractor_processor)
    return extractor_processors
