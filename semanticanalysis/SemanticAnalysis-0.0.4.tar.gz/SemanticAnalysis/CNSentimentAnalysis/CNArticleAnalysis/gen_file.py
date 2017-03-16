#!/usr/bin/python
#encoding=utf-8

input_file = file("test.txt", "r")
output_file = file("new.txt", "w")

lines = input_file.readlines()
counter  = 0
while counter < 10000:
    for line in lines:
        output_file.write(line)
    counter += 1

input_file.close()
output_file.close()
