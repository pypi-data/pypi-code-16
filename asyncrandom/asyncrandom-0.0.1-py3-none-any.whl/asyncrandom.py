#!/usr/bin/env python
"""Provides utils for interacting with the ANU Quantum Random Numbers Server.

Allows tornado applications to fetch one more more random numbers from the
ANU Quantum Random Numbers Server by calling the endpoint at
https://qrng.anu.edu.au/API/jsonI.php. The request is executed asynchronously
using the tornado networking framework.

More information about how the numbers are generated can be found on
https://qrng.anu.edu.au/.

Requires tornado and its IOLoop to run.

A simple example of generating a single random ``uint8``:

    def handle_random_int(f):
        print(f.result())

    f = asyncrandom.fetch()
    f.add_done_callback(handle_random_int)

    tornado.ioloop.IOLoop.current().start()

Multiple numbers can be generated as well. In this example we generate 10:

    def handle_random_int(f):
        print(f.result())

    f = asyncrandom.fetch(10)
    f.add_done_callback(handle_random_int)

    tornado.ioloop.IOLoop.current().start()

By default 8-bit unsigned integers are generated. Optionally, this can be
changed to 16-bit. Example of generating 10 16-bit integers:

    def handle_random_int(f):
        print(f.result())

    f = asyncrandom.fetch(10, asyncrandom.IntegerType.UINT16)
    f.add_done_callback(handle_random_int)

    tornado.ioloop.IOLoop.current().start()


If called from the command issues a request with ``length`` set to 1, and
``type`` set to ``"uint8"``, printing a single random int with a max value of
255. In this case, the call is synchronous.

Command line example:
    $ asyncrandom --int-type=uint8 --length=1
    105

Tested on Python versions:
    -2.7
    -3.4
    -3.5
    -3.6

"""
import argparse
from enum import Enum

from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import ioloop


__all__ = ["IntegerType", "fetch"]

URL = "https://qrng.anu.edu.au/API/jsonI.php"


class IntegerType(Enum):
    UINT8 = "uint8"
    UINT16 = "uint16"


@gen.coroutine
def fetch(length=1, int_type=IntegerType.UINT8):
    """Asynchronously generate one or more random numbers.

    Executes a GET request on https://qrng.anu.edu.au/API/jsonI.php with the
    ``length`` and ``type`` query arguments. Uses tornado's AsyncHTTPClient to
    make the request.

    Args:
        length (int): The number of random numbers to generate, corresponds to
            the ``length`` query argument for the HTTP request.
        int_type (asyncrandom.IntegerType): The type of the random numbers to
            generate. Possible options are ``"uint8"`` value of 255) or
            ``"uint16"`` (max value of 65,535).
            Corresponds to the ``type`` query argument for the HTTP request.

    Returns:
        tornado.concurrent.Future: a Future whose result is the randomly
            generated ``int`` if ``length`` is set to 1, or a ``list`` of
            randomly generated ``int`` otherwise.

    Raises:
        tornado.httpclient.HTTPError: raised in case of a non-200 status code in
            the HTTP response

        TypeError: in case ``length`` or ``int_type`` are of the wrong type

        ValueError: in case the HTTP response body contains
            ``{"sucess": false}``
    """
    if not isinstance(int_type, IntegerType):
        raise TypeError("int_type must be a asyncrandom.IntegerType")

    if not isinstance(length, int) or length <= 0:
        raise TypeError("length must be a positive non-zero int")

    client = httpclient.AsyncHTTPClient()
    url = URL + "?length={}&type={}".format(length, int_type.value)
    response = yield client.fetch(url)

    if response.error:
        raise response.error

    body = escape.json_decode(response.body)
    if not body["success"]:
        raise ValueError("The server failed to generate random number")

    value = body["data"]

    if len(value) == 1:
        value = value[0]

    raise gen.Return(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--length",
                        type=int,
                        default=1,
                        metavar='N',
                        help="how many numbers to generate")
    parser.add_argument("--int-type",
                        type=IntegerType,
                        default=IntegerType.UINT8,
                        help="the type of numbers to generate, uint8 or uint16")
    args = parser.parse_args()
    value = ioloop.IOLoop.current().run_sync(
        lambda: fetch(args.length, args.int_type))

    if isinstance(value, list):
        print(" ".join(map(str, value)))
    else:
        print(value)

if __name__ == "__main__":
    main()
