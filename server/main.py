import asyncio
import logging
import os
import random
import signal
import uuid
from typing import Optional

import asyncclick as click
import grpc.aio
import redis.asyncio as redis

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.meteo_utils import MeteoDataProcessor
from proto.services.processing import processing_service_pb2_grpc
from proto.services.registration.registration_service_pb2 import RegisterRequest, UID
from proto.services.registration.registration_service_pb2_grpc import RegistrationServiceStub
from server.processing_service import ProcessingService
from server.processing_service_servicer import ProcessingServiceServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = random.randint(50000, 60000)

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('load-balancer-address', type=str, required=False,
                default=os.environ.get("LOAD_BALANCER_ADDRESS"))
@click.argument('redis-address', type=str, required=False,
                default=os.environ.get("REDIS_ADDRESS"))
@click.option('--self-address', type=str, help="Set the self address")
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default=os.environ.get('LOG_LEVEL', 'info'), help="Set the log level")
@click.option('--port', type=int, help="Set the port", default=os.environ.get("PORT", DEFAULT_PORT))
async def main(
        load_balancer_address: str,
        redis_address: str,
        port: int,
        log_level: str,
        self_address: Optional[str] = None,
        debug: bool = False,
):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    if not load_balancer_address:
        raise ValueError("Load balancer address must be provided")

    if not redis_address:
        raise ValueError("Redis address must be provided")

    logger.info("Starting processing server")

    # register with load balancer
    logger.info("Registering with load balancer")

    registration = RegistrationServiceStub(grpc.insecure_channel(load_balancer_address))
    uid = uuid.uuid4().hex
    registration.Register(RegisterRequest(uid=uid, address=self_address, port=int(port)))

    # Create a gRPC server
    logger.info("Creating gRPC server")

    server = grpc.aio.server()

    logger.info("Creating services")

    # Create ProcessingService
    processing_service = ProcessingService(MeteoDataProcessor(), redis.from_url(redis_address, db=0))

    # Register the ProcessingService
    logger.info("Registering ProcessingServiceServicer")
    processing_service_pb2_grpc.add_ProcessingServiceServicer_to_server(
        ProcessingServiceServicer(processing_service),
        server
    )

    # Listen on port
    logger.info("Starting gRPC server")
    server.add_insecure_port(f"[::]:{port}")
    await server.start()

    logger.info("gRPC server started successfully")
    logger.info(f"Listening on port {port}")

    async def _cleanup():
        logger.info("Cleaning up")
        logger.info("Unregistering from load balancer")
        registration.Unregister(UID(uid=uid))
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

    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda: asyncio.create_task(_finish()))

    try:
        loop.run_until_complete(main.main())
    finally:
        logger.info("Received keyboard interrupt, shutting down")
        _finish()
