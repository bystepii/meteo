import logging
import os
import random
import time
import uuid
from concurrent import futures
from typing import Optional

import click
import grpc

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from proto.services.registration.registration_service_pb2 import RegisterRequest, UID
from proto.services.registration.registration_service_pb2_grpc import RegistrationServiceStub
from proto.services.terminal import terminal_service_pb2_grpc
from terminal.terminal_service import TerminalService
from terminal.terminal_service_servicer import TerminalServiceServicer

logger = logging.getLogger(__name__)

DEFAULT_PORT = random.randint(50000, 60000)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('proxy-address', type=str, required=False,
                default=os.environ.get("PROXY_ADDRESS"))
@click.option('--self-address', type=str, help="Set the self address")
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default=os.environ.get('LOG_LEVEL', 'info'), help="Set the log level")
@click.option('--port', type=int, help="Set the port", default=os.environ.get("PORT", DEFAULT_PORT))
def main(
        proxy_address: str,
        log_level: str,
        port: int,
        self_address: Optional[str] = None,
        debug: bool = False,
):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    logger.info("Starting load balancer")

    # register with proxy
    logger.info("Registering with proxy server")
    registration = RegistrationServiceStub(grpc.insecure_channel(proxy_address))
    uid = uuid.uuid4().hex
    registration.Register(RegisterRequest(uid=uid, address=self_address, port=int(port)))

    # Create a gRPC server
    logger.info("Creating gRPC server")
    server = grpc.server(futures.ThreadPoolExecutor())

    logger.info("Creating services")

    # Create TerminalService
    terminal_service = TerminalService()

    # Register the TerminalService
    logger.info("Registering TerminalServiceServicer")
    terminal_service_pb2_grpc.add_TerminalServiceServicer_to_server(
        TerminalServiceServicer(terminal_service),
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
