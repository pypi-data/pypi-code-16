"""App

The Sebureem web-server based on Bottle

"""
from flask import url_for, redirect, request, render_template, json
from playhouse.shortcuts import model_to_dict

from sebureem import app, db
from sebureem.models import *

__all__ = ['serve']

@app.route('/comments/<topic>', methods=['GET', 'POST'])
def comment(topic):
    if request.method == 'POST':
        print(request.form)
        comment_text = request.form['text']
        print("Adding comment to topic {} : {}".format(topic, comment_text))

        db.connect()
        sebuks, created = Sebuks.get_or_create(name=topic)
        sebura = Sebura.create(
                topic = sebuks, 
                text = comment_text
                )
        db.close()

    db.connect()
    sebureem = Sebura.select().join(Sebuks).where(Sebuks.name == topic)
    db.close()

    return render_template('sebureem.html', topic=topic, comments=sebureem) 

# Routes for managing comments
@app.route('/api/<topic>', methods=['GET'])
def get_comments(topic):
    """Get all comments for a given subject
    """
    print("Fetching comments for topic {}".format(topic))

    db.connect()
    sebuks = Sebuks.get(Sebuks.name == topic)
    db.close()
    
    return json.jsonify(model_to_dict(sebuks, backrefs=True))

@app.route('/api/<topic>', methods=['POST'])
def post_comment(topic):
    """Post a comment to a given subject
    """
    print(request.form)
    comment_text = request.form['text']
    print("Adding comment to topic {} : {}".format(topic, comment_text))

    db.connect()
    sebuks = Sebuks.get(Sebuks.name == topic)
    sebura = Sebura.create(
        topic = sebuks, 
        text = comment_text
    )
    db.close()
    return redirect(url_for('get_comments', topic=topic))

@app.route('/api/<topic>/<id>', methods=['GET'])
def edit_comment(topic, id):
    """Edit a given comment
    """
    return redirect(url_for('get_comments', topic=topic))

@app.route('/api/<topic>/<id>', methods=['GET'])
def delete_comment(topic, id):
    """Delete a given comment
    """
    return redirect(url_for('get_comments', topic=topic))

def serve(host='localhost', port=8080, debug=False):
    if debug:
        app.run(host, int(port), debug=True)
    else:
        app.run(host, int(port))

