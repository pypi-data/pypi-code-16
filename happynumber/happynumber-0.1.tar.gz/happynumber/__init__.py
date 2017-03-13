"""
This module allows you to find out if a number is happy or not, also sometimes
known as cool number. 
"""
import math

def _split_a_number(n):
    digit_list = [int(str(n)[x]) for x in range(int(math.log10(n))+1)]
    return digit_list

def _square_numbers_list(digit_list):
    squared_numbers = [math.pow(digit, 2) for digit in digit_list]
    #sum_of_squared_numbers = reduce(lambda x, y: x+y, squared_numbers)
    return sum(squared_numbers)

def is_happy_number(n):
    if n == 1:
        return True
    if n == 0:
        return False
    # for the number of digits, square each digit
    while n != 1:
        digit_list = _split_a_number(n)
        squared_sum = _square_numbers_list(digit_list)

        if squared_sum == 4:
            return False
        else:
            n = int(squared_sum)
    if n == 1:
        return True
