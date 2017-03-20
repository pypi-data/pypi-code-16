
import logging
import asyncio
import mugen

import uvloop

logging.basicConfig(level=logging.DEBUG)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from utils import gen_cookies

headers = {
'Connection': 'keep-alive',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, sdch',
}


async def task1():
    resp = await mugen.get('https://httpbin.org/ip')
    print(list(resp.headers.items()))
    print(resp.text)
    print(len(resp.content))
    print(resp.json())


loop = asyncio.get_event_loop()
tasks = asyncio.wait([task1()])
loop.run_until_complete(tasks)

