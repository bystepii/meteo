import logging
import os
import random
import time
import uuid
from concurrent import futures
from typing import Optional

import click
import grpc
import redis

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.meteo_utils import MeteoDataProcessor
from proto.services.processing import processing_service_pb2_grpc
from proto.services.registration.registration_service_pb2 import RegisterRequest, UID
from proto.services.registration.registration_service_pb2_grpc import RegistrationServiceStub
from server.processing_service import ProcessingService
from server.processing_service_servicer import ProcessingServiceServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = random.randint(50000, 60000)


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
def main(
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
    server = grpc.server(futures.ThreadPoolExecutor())

    logger.info("Creating services")

    # Create ProcessingService
    processing_service = ProcessingService(MeteoDataProcessor(), redis.from_url(redis_address, db=0))

    # Register the ProcessingService
    logger.info("Registering ProcessingServiceServicer")
    processing_service_pb2_grpc.add_ProcessingServiceServicer_to_server(
        ProcessingServiceServicer(processing_service),
        server
    )

    # Listen on port 50051
    logger.info("Starting gRPC server")
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    logger.info("gRPC server started successfully")
    logger.info(f"Listening on port {port}")

    # Keep the server running
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        registration.Unregister(UID(uid=uid))


if __name__ == '__main__':
    main()
