import scriptcrypt.db as db
import scriptcrypt.settings as setts
import json

def run(path):
    mset = setts.Settigns()
    settings = mset.readSettings()
    mydb = db.dbHandler("sqlite:///" + settings["db"])
    dump = [mydb.entryInfo(name) for name in mydb.entryNames()]
    with open(path, "w") as f:
        f.write(json.dumps(dump,
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': ')))

