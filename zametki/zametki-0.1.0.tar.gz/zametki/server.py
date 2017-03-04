import io, os
from zametki import post as postlib

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def listposts():
    posts = postlib.getPosts(os.listdir("./_posts"))

    return render_template('listpost.html', posts = posts)



@app.route("/posts/<postid>")
def view_post(postid):
    posts = postlib.getPosts(os.listdir("./_posts"))
    maxlength = len(posts)
    post = postlib.getCurrentPost(posts, int(postid) - 1, html = True)
    
    if (post == None):
        return "Post does not exist"
    postId = int(postid)

    return render_template('readpost.html', post = post, postid = postId, maxlen = maxlength)

def main():
  app.run(debug=True)