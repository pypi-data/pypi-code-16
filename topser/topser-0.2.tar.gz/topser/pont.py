from markdown import markdown

def pont():
    msg = markdown(u'I am **ponting**')
    print(msg)
    return (msg)