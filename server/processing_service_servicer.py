import logging

from grpc import ServicerContext

from google.protobuf.empty_pb2 import Empty

from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from proto.services.processing import processing_service_pb2_grpc
from server.processing_service import ProcessingService

logger = logging.getLogger(__name__)


class ProcessingServiceServicer(processing_service_pb2_grpc.ProcessingServiceServicer):
    def __init__(self, processing_service: ProcessingService):
        logger.info("Initializing ProcessingServiceServicer")
        self._processing_service = processing_service

    def ProcessMeteoData(self, meteo_data: RawMeteoData, context: ServicerContext) -> Empty:
        logger.info(f"{context.peer()} called ProcessMeteoData")
        self._processing_service.process_meteo_data(meteo_data)
        return Empty()

    def ProcessPollutionData(self, pollution_data: RawPollutionData, context: ServicerContext) -> Empty:
        logger.info(f"{context.peer()} called ProcessPollutionData")
        self._processing_service.process_pollution_data(pollution_data)
        return Empty()
