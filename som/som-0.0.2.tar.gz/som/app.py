from flask import (
    Flask, 
    render_template, 
    request
)

from flask_restful import Resource, Api
from werkzeug import secure_filename
import webbrowser
import tempfile
import shutil
import random
import os

# SERVER CONFIGURATION ##############################################
class SomServer(Flask):

    def __init__(self, *args, **kwargs):
        super(SomServer, self).__init__(*args, **kwargs)

        # Set up temporary directory on start of application
        self.tmpdir = tempfile.mkdtemp()
        self.images = None # List of images for visualization


# API VIEWS #########################################################
# eventually we can have views or functions served in this way...

app = SomServer(__name__)
#api = Api(app)    
#api.add_resource(apiExperiments,'/experiments')
#api.add_resource(apiExperimentSingle,'/experiments/<string:exp_id>')

# BAR PLOTS TO COMPARE TO PACKAGES #################################
@app.route('/som/annotate')
def annotate_images():
    return render_template('annotate_images.html')


# START FUNCTIONS ##################################################
    
# Function to make single package/image tree
def make_tree(image,port=None,sudopw=None):
    app.image = image
    app.sudopw = sudopw
    if port==None:
        port=8088
    print("It goes without saying. I suspect now it's not going.")
    webbrowser.open("http://localhost:%s/container/tree" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)


# Function to make bar chart to compare to os
def plot_os_sims(image,port=None,sudopw=None):
    app.image = image
    app.sudopw = sudopw
    if port==None:
        port=8088
    print("The not remembering is part of the disability, my dear fish.")
    webbrowser.open("http://localhost:%s/container/os" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)


# Function to make similar tree to compare images
def make_sim_tree(image1,image2,port=None):
    app.images = [image1,image2]
    if port==None:
        port=8088
    print("The recipe for insight can be reduced to a box of cereal and a Sunday afternoon.")
    webbrowser.open("http://localhost:%s/containers/similarity" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)

# Function to make difference tree for two images
def make_diff_tree(image1,image2,port=None):
    app.images = [image1,image2]
    if port==None:
        port=8088
    print("Pandas... just let them go.")
    webbrowser.open("http://localhost:%s/containers/subtract" %(port))
    app.run(host="0.0.0.0",debug=True,port=port)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
