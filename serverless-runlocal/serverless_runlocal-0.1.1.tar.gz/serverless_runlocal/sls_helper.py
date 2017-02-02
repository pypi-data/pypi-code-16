import importlib
from flask_helper import flaskify

# parse 'parameter key set from string like aaa/{user_id/xxx/{app_id}'


def extract_params_from_str(s, start_ident='{', end_ident='}'):
    c = set()
    idx = s.find(start_ident)
    while(0 < idx):
        lst_idx = s.find(end_ident)
        if lst_idx < 0:
            return c
        c.add(s[idx + 1:lst_idx])
        s = s[lst_idx + 1:]
        idx = s.find(start_ident)
    return c

# return function object takes *args, returning *args
# TODO: is it really needed? just lambda function seems to be enough..


def make_func(*args):
    def _function(*args):
        pass
    return _function

# organize path parameter to pass to function


def format_path_param(path):
    if not path.startswith('/'):
        path = '/' + path
    path = path.replace('{', '<')
    path = path.replace('}', '>')
    return path


def get_lambda_function(sls_handler_path):
    module, function = sls_handler_path.split('.')
    module = importlib.import_module(module.replace('/', '.'))
    function = getattr(module, function)
    return function


# public


def parse_serverless_config(app, sls, swagger_doc_dir=None):
    if swagger_doc_dir:
        import os
        from flasgger.utils import swag_from

    for function_name, function_body in sls['functions'].iteritems():
        function_object = get_lambda_function(function_body['handler'])
        http_events = [d for _, d in enumerate(
            function_body['events']) if 'http' in d]
        for e in http_events:
            method = e['http']['method']
            path = format_path_param(e['http']['path'])
            params = tuple(extract_params_from_str(path))

            #  print (function_name, path, params)
            view_function = make_func(params)

            if swagger_doc_dir:
                # load functio_name + /yml under swagger_doc_dir
                fpath = os.path.join(swagger_doc_dir, function_name + '.yml')

                if not os.path.isabs(fpath):
                    print 'sorry, you have to path absolute path as swagger_doc_dir.'
                    pass

                if os.path.exists(fpath):
                    view_function = swag_from(fpath)(view_function)
                    print 'flassger: loading %s' % fpath
                else:
                    # ignore if not available
                    pass

            view_function = flaskify(function_object)(view_function)

            app.add_url_rule(
                path,
                endpoint=function_name,
                view_func=view_function,
                methods=[method.upper()])
    print app.url_map
    return app
