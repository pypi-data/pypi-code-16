import asyncio
import logging

from juju.model import Model


async def run():
    model = Model()
    await model.connect_current()

    await model.deploy(
        '/tmp',
    )

    await model.disconnect()
    model.loop.stop()


logging.basicConfig(level=logging.DEBUG)
ws_logger = logging.getLogger('websockets.protocol')
ws_logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
loop.set_debug(False)
loop.create_task(run())
loop.run_forever()
