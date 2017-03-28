import time
time.sleep(3)
print("DO 10")
with open('myfile_10.txt', 'w') as tmp:
    tmp.write('10')
