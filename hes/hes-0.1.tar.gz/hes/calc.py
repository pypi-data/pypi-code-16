#!/usr/bin/env python3
permitted = "0123456789+-/*= "

print("""
######## Calculator ########
#    Permitted operators   #
#            +             #
#            -             #
#            *             #
#            /             #
############################
""")

while True:
    data = input("Calculate: ")
    for s in data:
        if s not in permitted:
            quit()

    res = eval(data)

    print(res)
