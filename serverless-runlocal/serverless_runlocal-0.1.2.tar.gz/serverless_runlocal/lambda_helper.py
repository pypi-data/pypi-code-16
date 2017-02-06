import json

N = 'NOT_IMPLEMENTED'


def get_event(request):
    body = json.dumps(request.get_json())
    resource = request.path
    requestContext = {
        "resourceId": N,
        "apiId": N,
        "resourcePath": request.path,
        "httpMethod": request.method,
        "requestId": N,
        "accountId": N,
        "identity": {
            "apiKey": N,
            "userArn": N,
            "cognitoAuthenticationType": N,
            "accessKey": N,
            "caller": N,
            "userAgent": request.headers.get('User-Agent'),
            "user": N,
            "cognitoIdentityPoolId": N,
            "cognitoIdentityId": N,
            "cognitoAuthenticationProvider": N,
            "sourceIp": "111.111.111.111",
            "accountId": N,
        }
    }
    queryStringParameters = None
    path = request.path
    httpMethod = request.method
    pathParameters = {}
    isBase64Encoded = False
    stageVariables = None

    event = dict(
        body=body,
        resource=resource,
        requestContext=requestContext,
        queryStringParameters=queryStringParameters,
        headers=dict(request.headers),
        pathParameters=pathParameters,
        httpMethod=httpMethod,
        isBase64Encoded=isBase64Encoded,
        path=path,
        stageVariables=stageVariables
    )
    return event


def get_context(request):
    raise NotImplementedError('TODO')
