import markdown2

def createPostFile(postName):
    post = open("_posts/" + postName, "w", encoding = "utf-8")
    post.write("")
    post.close()
    print("success!")

def getPosts(rawPosts):

    posts = rawPosts

    for i in range (0, len(posts) - 1):
        if (posts[i] == ".gitlock"):
            posts.pop(i)
            
            break
        else: 
            continue

    if (posts[0] == ".gitlock"):
        return []
    else:
        return posts

def getCurrentPost(posts, postId, html=False):
    if int(postId) < 0:
        print ("Id can not be below zero")
        return None

    try:
        postName = posts[int(postId)]
        postFile = open("./_posts/" + postName, "r", encoding= "utf-8")
        rawPostData = ''.join(postFile.readlines())
        
        if (html == True):
            htmlData = markdown2.markdown(rawPostData)
            return htmlData
        elif (html == False):
            return rawPostData
    
    except Exception:
        print ("not a number or incorrect index")
        return None
