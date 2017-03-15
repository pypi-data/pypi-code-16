def aml_cli_get_sample_request():
    import json
    sampleDF = spark.read.schema(inputSchema).json('PLACEHOLDER')
    sampleRequest = json.loads(sampleDF.toJSON().first())
    retVal = [sampleRequest[k] for k in sampleDF.columns]
    return '[{}]'.format(json.dumps(retVal))
