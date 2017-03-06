#!/bin/python

from setuptools import setup

setup(  name        = "roomai",
        version     = "0.1a3",
        description = "Some chess environments with some base AI players for developing new AI players",
        url         = "https://github.com/algorithmdog/RoomAI/tree/0.1a3",
        author      = "AlgorithmDog",
        author_email= "lili1987mail@gmail.com",
        license     = "MIT",
        packages    = ["roomai","roomai.doudizhu","roomai.kuhn"],
        zip_safe    = False)
