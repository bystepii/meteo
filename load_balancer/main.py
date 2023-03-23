import logging
import os
import time
from concurrent import futures
from typing import Optional

import click
import grpc

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.registration_service import RegistrationService
from common.registration_service_servicer import RegistrationServiceServicer
from load_balancer.load_balancer import LoadBalancer
from load_balancer.meteo_service import MeteoService
from load_balancer.meteo_service_servicer import MeteoServiceServicer
from proto.services.meteo import meteo_service_pb2_grpc
from proto.services.registration import registration_service_pb2_grpc

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50051


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default='info', help="Set the log level")
@click.option('--port', type=int, help="Set the port")
def main(debug: bool = False, log_level: str = 'info', port: Optional[int] = None):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    port = port or os.environ.get("PORT", DEFAULT_PORT)

    logger.info("Starting load balancer")

    # Create a gRPC server
    logger.info("Creating gRPC server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    logger.info("Creating services")

    # Create RegistrationService
    registration_service = RegistrationService(parent_service="LoadBalancer")

    # Create load balancer
    load_balancer = LoadBalancer(registration_service)

    # Create MeteoService
    meteo_service = MeteoService(load_balancer, registration_service)

    # Register the MeteoService
    logger.info("Registering MeteoServiceServicer")
    meteo_service_pb2_grpc.add_MeteoServiceServicer_to_server(
        MeteoServiceServicer(meteo_service),
        server
    )

    # Register the RegistrationService
    logger.info("Registering RegistrationServiceServicer")
    registration_service_pb2_grpc.add_RegistrationServiceServicer_to_server(
        RegistrationServiceServicer(registration_service),
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
