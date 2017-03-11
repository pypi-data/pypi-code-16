import re
with open("log", "r+") as f:
    log_content = f.read()
    find_entries = re.search(r"\[(\d{1,3} entries)|(1 entry)\]", log_content)
    if find_entries:
        print(find_entries.group(1))
        print(6666666666666)
    else:
        print("bad")
        #self.output.good_print("can not get any entries from log file,I will return 0", 'red')


