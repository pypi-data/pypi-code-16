import scriptcrypt.db as db
import json

def run(path2read, path2write):
    with open(path2read, "r") as f:
        dump = f.read()
    data = json.loads(dump)

    mydb = db.dbHandler("sqlite:///" + path2write)
    for entry in data:
        mydb.create()
        mydb.addEntry(entry)
