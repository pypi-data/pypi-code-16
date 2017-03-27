import string
import random

# 26 lower case letters + 26 upper case letters + 10 numbers
# means 62 possible random_char
def random_char():
    letters = string.letters
    numbers = '1234567890'
    all_chars = letters + numbers
    char = random.choice(all_chars)
    return char

# 62 possible values for each character and 32 characters means there
# exists 62^32 possible access tokens.
# That's 2 followed by 57 0s.
# That number is 2 octodecillion.
# That is more atoms than there are on Earth.
# This is the same number of stars as 2000000000000000000000000 universes.
def random_access_token():
    access_token = ''
    for _ in range(64):
        access_token += random_char()
    return access_token
