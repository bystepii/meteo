import asyncio
import logging

from google.protobuf.empty_pb2 import Empty
from grpc import ServicerContext

from meteo_service import MeteoService
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from proto.services.meteo import meteo_service_pb2_grpc

logger = logging.getLogger(__name__)


class MeteoServiceServicer(meteo_service_pb2_grpc.MeteoServiceServicer):
    def __init__(self, meteo_service: MeteoService):
        logger.info("Initializing MeteoServiceServicer")
        self._meteo_service = meteo_service
        self._background_tasks = set()

    async def SendMeteoData(self, meteo_data: RawMeteoData, context: ServicerContext) -> Empty:
        logger.info(f"{context.peer()} called SendMeteoData")
        task = asyncio.create_task(self._meteo_service.send_meteo_data(meteo_data))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return Empty()

    async def SendPollutionData(self, pollution_data: RawPollutionData, context: ServicerContext) -> Empty:
        logger.info(f"{context.peer()} called SendPollutionData")
        task = asyncio.create_task(self._meteo_service.send_pollution_data(pollution_data))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return Empty()
