import model

# Show the choices to user
HELPS = """lv1: countries
"""

def learn():
    lv = raw_input(HELPS)
    if not lv:
        lv = 'lv1'
    exec('from model import %s' % lv)
    exec('%s.start()' % lv)

learn()# TODO delete