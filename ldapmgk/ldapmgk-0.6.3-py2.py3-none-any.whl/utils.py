# -*- coding: utf-8 -*-

import random

r = random.SystemRandom()


def generate_password(words, top=2000, k=4, numbers=None, characters=None,
                      first_upper=True):
    """Return a random password based on a sorted word list."""
    elements = r.sample(words[:top], k)

    if numbers:
        elements.insert(r.randint(1, len(elements)), r.choice(numbers))
    if characters:
        elements.insert(r.randint(1, len(elements)), r.choice(characters))
    if first_upper:
        elements[0] = elements[0].title()

    return ''.join(elements)
