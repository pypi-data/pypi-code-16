#!/bin/python

from setuptools import setup

setup(  name        = "roomai",
        version     = "0.1a4",
        description = "A toolkit for developing and comparing chess-bots",
        url         = "https://github.com/algorithmdog/RoomAI/tree/0.1a3",
        author      = "AlgorithmDog",
        author_email= "lili1987mail@gmail.com",
        license     = "MIT",
        packages    = ["roomai","roomai.doudizhu","roomai.kuhn"],
        zip_safe    = False)
