import time
import logging
import grpc
from concurrent import futures

from common.log import setup_logger

from proto.services.meteo import meteo_service_pb2
from proto.services.meteo import meteo_service_pb2_grpc
from proto.services.registration import registration_service_pb2
from proto.services.registration import registration_service_pb2_grpc

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logger()
