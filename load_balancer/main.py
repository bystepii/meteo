import logging
import time
from concurrent import futures

import grpc

from common.log import setup_logger
from load_balancer.load_balancer import LoadBalancer
from load_balancer.meteo_service import MeteoService
from load_balancer.meteo_service_servicer import MeteoServiceServicer
from load_balancer.registration_service import RegistrationService
from load_balancer.registration_servicer import RegistrationServiceServicer
from proto.services.meteo import meteo_service_pb2_grpc
from proto.services.registration import registration_service_pb2_grpc

logger = logging.getLogger(__name__)


def main():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Create load balancer
    load_balancer = LoadBalancer()

    # Create RegistrationService
    registration_service = RegistrationService()

    # Create MeteoService
    meteo_service = MeteoService(load_balancer, registration_service)

    # Register the MeteoService
    meteo_service_pb2_grpc.add_MeteoServiceServicer_to_server(
        MeteoServiceServicer(meteo_service),
        server
    )

    # Register the RegistrationService
    registration_service_pb2_grpc.add_RegistrationServiceServicer_to_server(
        RegistrationServiceServicer(registration_service),
        server
    )

    # Listen on port 50051
    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    setup_logger()
    main()
