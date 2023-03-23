import logging
import os
import time
from concurrent import futures
from typing import Optional

import click
import grpc

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.meteo_utils import MeteoDataProcessor
from proto.services.processing import processing_service_pb2_grpc
from server.processing_service import ProcessingService
from server.processing_service_servicer import ProcessingServiceServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50051


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('load-balancer-address', type=str)
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default='info', help="Set the log level")
@click.option('--port', type=int, help="Set the port")
def main(
        load_balancer_address: Optional[str] = None,
        debug: bool = False,
        log_level: str = 'info',
        port: Optional[int] = None
):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    load_balancer_address = load_balancer_address or os.environ.get("LOAD_BALANCER_ADDRESS")
    if not load_balancer_address:
        raise ValueError("Load balancer address must be provided")
    port = port or os.environ.get("PORT", DEFAULT_PORT)

    logger.info("Starting processing server")

    # Create a gRPC server
    logger.info("Creating gRPC server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    logger.info("Creating services")

    # Create ProcessingService
    processing_service = ProcessingService(MeteoDataProcessor())

    # Register the ProcessingService
    logger.info("Registering ProcessingServiceServicer")
    processing_service_pb2_grpc.add_ProcessingServiceServicer_to_server(
        ProcessingServiceServicer(processing_service),
        server
    )

    # Listen on port 50051
    logger.info("Starting gRPC server")
    server.add_insecure_port("[::]:{}".format(port))
    server.start()

    logger.info("gRPC server started successfully")
    logger.info(f"Listening on port {port}")

    # Keep the server running
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()