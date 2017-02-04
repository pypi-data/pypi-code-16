"""Core."""
from flask import Blueprint, jsonify, request


class Hooker(object):
    """Docs here."""

    def __init__(self, app=None, name='hooker', url_prefix='/webhooks', methods=['GET', 'POST']):
        """Create the Hooker object."""
        self._app = app
        self._name = name
        self._methods = methods
        self._blueprint = Blueprint(name, __name__, url_prefix=url_prefix)
        self._event_handler = {}

        if app:
            self.init_app(app)

    def add_handler(self, event=None, func=None, event_type=None):
        """Add function to handle a specific event from an event_type."""
        if event and func and event_type:
            new_event = {event: func}

            if event_type not in self._event_handler:
                self._event_handler[event_type] = {}

            self._event_handler[event_type].update(new_event)
        else:
            print('All parameters are required.')

    def _run_handlers(self):
        if request.method == 'GET':
            return 'OK'
        for event_type in self._event_handler.keys():
            if event_type in request.headers and request.headers.get("Content-Type", '') == "application/json":
                try:
                    event = request.headers.get(event_type)
                    if event in self._event_handler[event_type].keys():
                        self._event_handler[event_type][event](request.json)
                    else:
                        print('event not allowed.')

                except Exception as e:
                    return (str(e))

                return jsonify({
                    'status': 'success',
                    'message': 'Event: %s, was triggered successfully' % event
                })
            else:
                pass
        return 'NO'

    def init_app(self, app):
        """Register the webhook."""
        self._blueprint.add_url_rule('', view_func=self._run_handlers, methods=self._methods)
        app.register_blueprint(self._blueprint)
