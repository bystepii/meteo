import asyncio
import logging
import os
import signal
from typing import Optional

import asyncclick as click
import grpc.aio
import redis.asyncio as redis

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.registration_service import RegistrationService
from common.registration_service_servicer import RegistrationServiceServicer
from proto.services.registration import registration_service_pb2_grpc
from proxy.tumbling_window import TumblingWindow

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50050

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('redis-address', type=str, required=False,
                default=os.environ.get("REDIS_ADDRESS"))
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default=os.environ.get('LOG_LEVEL', 'info'), help="Set the log level")
@click.option('--port', type=int, help="Set the port", default=os.environ.get("PORT", DEFAULT_PORT))
@click.option('--interval', type=int, help="Set the default tumbling window interval in ms")
async def main(
        redis_address: str,
        log_level: str,
        port: int,
        debug: bool = False,
        interval: Optional[int] = None,
):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    logger.info("Starting proxy server")

    # Create a gRPC server
    logger.info("Creating gRPC server")
    server = grpc.aio.server()

    logger.info("Creating services")

    # Create RegistrationService
    registration_service = RegistrationService(parent_service="Proxy")

    # Register the RegistrationService
    logger.info("Registering RegistrationServiceServicer")
    registration_service_pb2_grpc.add_RegistrationServiceServicer_to_server(
        RegistrationServiceServicer(registration_service),
        server
    )

    # Create the tumbling window
    tumbling_window = TumblingWindow(registration_service, redis.from_url(redis_address, db=0), interval)

    # Listen on port 50050
    logger.info("Starting gRPC server")
    server.add_insecure_port(f"[::]:{port}")
    await server.start()

    logger.info("gRPC server started successfully")
    logger.info(f"Listening on port {port}")

    async def _cleanup():
        logger.info("Cleaning up")
        logger.info("Shutting down gRPC server")
        await server.stop(5)

    _cleanup_coroutines.append(_cleanup())

    await server.wait_for_termination()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    async def _finish():
        logger.info("Shutting down")
        await asyncio.gather(*_cleanup_coroutines, return_exceptions=True)
        tasks = asyncio.all_tasks() - {asyncio.current_task()}
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Shutting down asyncio loop")
        loop.stop()
        loop.close()
        exit(0)


    background_tasks = set()


    def signal_handler(sig):
        logger.info(f"Received signal {sig}")
        task = asyncio.create_task(_finish())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)


    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda: signal_handler(s))

    try:
        loop.run_until_complete(main.main())
    finally:
        logger.info("Received keyboard interrupt, shutting down")
