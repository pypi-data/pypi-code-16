# maildrake/web/views.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Flask views for Mail Drake web app. """

import flask

from .. import config
from .. import store
from . import app
from . import logger


if config.options.DEBUG:
    app.debug = True
    app.pin_security = True
    app.pin_logging = True


def connect_db(database_file_path):
    """ Make a new connection to the database. """
    connection = store.sqlite.connect(database_file_path)
    return connection


@app.before_request
def before_request():
    """ Hook to set up for the incoming HTTP request. """
    flask.g.db = connect_db(flask.current_app.config['DATABASE'])


@app.teardown_request
def teardown_request(exception):
    """ Hook to tear down after the HTTP request.

        :param exception: The exception object which caused the
            request to end, or ``None`` if no exception occurred.
        :return: ``None``.

        """
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()


@app.route("/login", methods=['POST'])
def login_post():
    """ Flask view for a POST request to log in. """
    error = None
    if all([
            flask.request.form['username'] == app.config['USERNAME'],
            flask.request.form['passphrase'] == app.config['PASSPHRASE'],
    ]):
        flask.session['logged_in'] = True
        flask.flash("You are now logged in.")
        result = flask.redirect(flask.url_for('index'))
    else:
        error = "Invalid username and/or passphrase."
        result = flask.render_template("login.html", error=error)

    return result


@app.route("/login", methods=['GET'])
def login():
    """ Flask view for a GET request to log in. """
    result = flask.render_template("login.html")
    return result


@app.route("/logout")
def logout():
    """ Flask view for a GET request to log out. """
    flask.session.pop('logged_in', None)
    flask.flash("You are now logged out.")
    return flask.redirect(flask.url_for('message_list'))


@app.route("/")
def index():
    """ Flask view for the index page of the app. """
    result = flask.render_template("index.html")
    return result


@app.route("/messages")
def message_list():
    """ Flask view for the list of messages in the queue. """
    cursor = flask.g.db.cursor()
    cursor.execute("""
            SELECT
                rowid,
                message_id,
                created_at,
                "date",
                sender,
                recipients,
                subject,
                length(raw)
            FROM message
            ORDER BY
                created_at DESC
            """)
    messages = [row for row in cursor.fetchall()]
    result = flask.render_template(
            "message_list.html", messages=messages)
    return result


@app.route("/messages/<int:row_id>")
def message_detail(row_id):
    """ Flask view for the detail view of a message.

        :param row_id: Database row ID of the message.
        :return: The response object to send.

        """
    cursor = flask.g.db.cursor()
    cursor.execute("""
            SELECT
                message_id,
                created_at,
                "date",
                sender,
                recipients,
                subject,
                mime_type,
                body,
                length(raw) AS length,
                raw
            FROM message
            WHERE
                rowid = :row_id
            """, {
                'row_id': row_id,
            })
    message = cursor.fetchone()
    result = flask.render_template(
            "message_detail.html", message=message)
    return result


@app.route("/messages/clear")
def message_clear():
    """ Flask view for deleting all messages from the queue. """
    cursor = flask.g.db.cursor()
    cursor.execute("""
            DELETE FROM message
            """)
    flask.g.db.commit()
    flask.flash("All messages deleted from the queue.")
    return flask.redirect(flask.url_for('message_list'))


# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
