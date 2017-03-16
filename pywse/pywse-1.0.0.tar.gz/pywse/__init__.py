import model

# Show the choices to user
HELPS = """lv1: countries
"""

def learn():
    lv = raw_input(HELPS)
    exec('from model import %s' % lv)
    exec('%s.start()' % lv)

learn()# TODO delete