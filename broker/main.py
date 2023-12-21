import logging
import asyncio
import os
from amqtt.broker import Broker


async def broker_coro():
    config = {
        'listeners': {
            'default': {
                'type': 'tcp',
                'bind': '0.0.0.0:47688',
            },
            'ws-mqtt': {
                'bind': '127.0.0.1:8080',
                'type': 'ws',
                'max_connections': 10,
            },
        },
        'sys_interval': 10,
        'auth': {
            'allow-anonymous': True,
            'password-file': os.path.join(os.path.dirname(os.path.realpath(__file__)), "passwd"),
            'plugins': [
                'auth_file', 'auth_anonymous'
            ]
        },
        'topic-check': {
            'enabled': False
        }
    }

    broker = Broker(config)
    await broker.start()


if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(broker_coro())
    asyncio.get_event_loop().run_forever()