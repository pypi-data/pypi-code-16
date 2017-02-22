from argparse import ArgumentParser
from flask import Flask, abort, send_from_directory
import json
import logging
import os

app = Flask(__name__)
log = logging.getLogger(__name__)
packages = {}


@app.route('/<package>/<version>/<database>/<collection>/index.<extension>')
def serve_index(package, version, database, collection, extension):
    # Find database
    if package not in packages or version not in packages[package]:
        abort(404)

    path = os.path.join(packages[package][version], database, collection)

    # Ensure index exists
    filename = 'index.%s' % extension

    if not os.path.exists(os.path.join(path, filename)):
        abort(404)

    # Serve file
    mimetype = None

    if extension.endswith('json'):
        mimetype = 'application/json'

    return send_from_directory(path, filename, mimetype=mimetype)


@app.route('/<package>/<version>/<database>/<collection>/items/<key>.<extension>')
def serve_item(package, version, database, collection, key, extension):
    # Find database
    if package not in packages or version not in packages[package]:
        abort(404)

    path = os.path.join(packages[package][version], database, collection, 'items')

    # Ensure index exists
    filename = '%s.%s' % (key, extension)

    if not os.path.exists(os.path.join(path, filename)):
        abort(404)

    # Serve file
    mimetype = None

    if extension.endswith('json'):
        mimetype = 'application/json'

    return send_from_directory(path, filename, mimetype=mimetype)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('-p', '--package', action='append')

    args = parser.parse_args()

    for path in args.package:
        name = os.path.basename(path)
        module = name.replace('-', '_')

        # Ensure package has a "package.json" file
        details_path = os.path.join(path, module, 'package.json')

        if not os.path.exists(details_path):
            log.warn('[%s] No package details found at %r', name, details_path)
            continue

        # Read package details
        with open(details_path, 'rb') as fp:
            details = json.load(fp)

        # Retrieve package version
        version = details.get('version')

        if not version:
            log.warn('Package %r has an invalid version defined (%r)', path, version)
            continue

        log.info('[%s] (v%s) - Found package at: %r', name, version, path)

        # Update `packages` dictionary
        if name not in packages:
            packages[name] = {}

        packages[name][version] = path

    # Run server
    app.run(debug=False)
