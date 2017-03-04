import os

import datetime
from datetime import date

from zametki import server

from zametki import post as postlib

def main(arguments):
    
    if (arguments["runserver"] == True):
        print ("preparing to run zametki")
        server.main()

    elif (arguments["posts"] == True):
        print ("listing posts:")
        posts = postlib.getPosts(os.listdir("./_posts"))

        for i in range(0, len(posts)):
            postName = posts[i]
            print (str(i+1) + ") " + postName[0: len(postName)-3])

        if len(posts) == 0:
            print ("There are currently no posts")

    elif (arguments["readpost"] == True):
        try:
            postId = int(arguments["<postId>"]) - 1
            posts = postlib.getPosts(os.listdir("./_posts"))

            post = postlib.getCurrentPost(posts, postId)

            if (post == None):
                print ("post id cannot be below zero")
            else:
                if (post == ""):
                    print ("empty file")
                else:
                    print (post)

        except Exception:
            print ("please check that the post entry exists and that the post id is a integer")
        

    elif (arguments["generate-post"] == True):
        postname = arguments["<postname>"] 
        todaysDate = date.today()
        fileExtension = ".md"
        completePostFile = postname + "-" + str(todaysDate) + fileExtension
        postlib.createPostFile(completePostFile)

