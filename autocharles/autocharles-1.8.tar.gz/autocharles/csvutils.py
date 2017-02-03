import csv
import keys

def writeCSV(output, activity_list):
    f = open(output, 'wb')
    w = csv.DictWriter(f, keys.keys)
    w.writeheader()
    for item in activity_list:
        w.writerow(item)
    f.close()
