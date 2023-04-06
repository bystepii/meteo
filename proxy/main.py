import logging
import os
import time
from concurrent import futures
from typing import Optional

import click
import grpc
import redis

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.registration_service import RegistrationService
from common.registration_service_servicer import RegistrationServiceServicer
from proto.services.registration import registration_service_pb2_grpc
from proxy.tumbling_window import TumblingWindow

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50050


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('redis-address', type=str, required=False,
                default=os.environ.get("REDIS_ADDRESS"))
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default=os.environ.get('LOG_LEVEL', 'info'), help="Set the log level")
@click.option('--port', type=int, help="Set the port", default=os.environ.get("PORT", DEFAULT_PORT))
@click.option('--interval', type=int, help="Set the default tumbling window interval in ms")
def main(
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
    server = grpc.server(futures.ThreadPoolExecutor())

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
    server.start()

    logger.info("gRPC server started successfully")
    logger.info(f"Listening on port {port}")

    # Keep the server running
    try:
        while True:
            tumbling_window.run()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()
