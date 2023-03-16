import logging

from google.protobuf.empty_pb2 import Empty

from load_balancer.meteo_service import MeteoService
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from proto.services.meteo import meteo_service_pb2_grpc

logger = logging.getLogger(__name__)


class MeteoServiceServicer(meteo_service_pb2_grpc.MeteoServiceServicer):
    def __init__(self, meteo_service: MeteoService):
        logger.info("Initializing MeteoServiceServicer")
        self._meteo_service = meteo_service

    def SendMeteoData(self, meteo_data: RawMeteoData, context) -> Empty:
        logger.debug(f'Received meteo data {meteo_data}')
        self._meteo_service.send_meteo_data(meteo_data)
        return Empty()

    def SendPollutionData(self, pollution_data: RawPollutionData, context) -> Empty:
        logger.debug(f'Received pollution data {pollution_data}')
        self._meteo_service.send_pollution_data(pollution_data)
        return Empty()
