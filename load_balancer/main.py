import logging
import time
from concurrent import futures

import grpc

from common.log import setup_logger
from common.registration_service import RegistrationService
from load_balancer.lb import LoadBalancer
from load_balancer.meteo_service import MeteoService
from load_balancer.meteo_service_servicer import MeteoServiceServicer
from load_balancer.registration_servicer import RegistrationServiceServicer
from proto.services.meteo import meteo_service_pb2_grpc
from proto.services.registration import registration_service_pb2_grpc

logger = logging.getLogger(__name__)


def main():
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
    server.add_insecure_port('[::]:50051')
    server.start()

    logger.info("gRPC server started successfully")

    # Keep the server running
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    setup_logger()
    main()
