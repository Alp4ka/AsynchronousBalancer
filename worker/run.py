import asyncio

from uvicorn import Config, Server

import views
import argparse


async def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--host', type=str, required=False, default='0.0.0.0')
    arg_parser.add_argument('--port', type=int, required=False, default=8000)
    args = arg_parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    config = Config(app=views.app, loop=loop, port=args.port, host=args.host, reload=False)  # noqa
    server = Server(config)

    await asyncio.gather(
        server.serve(),
        views.get_worker().periodically_log_connections(10)
    )


if __name__ == "__main__":
    asyncio.run(main())
