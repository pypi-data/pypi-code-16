import model

# Show the choices to user
HELPS = """1: Practice countries
2: Which country do you want to practice
Waiting for your input (such as 1): """

def learn():
    while True:
        try:
            lv = raw_input(HELPS)
            if not lv:
                lv = '1'
            lv = 'lv' + lv
            exec('from model import %s' % lv)
            exec('%s.start()' % lv)
            break
        except:
            pass
