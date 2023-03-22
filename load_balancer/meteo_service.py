import logging

from common.registration_service import RegistrationService
from load_balancer.lb import LoadBalancer
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData

logger = logging.getLogger(__name__)


class MeteoService:
    def __init__(self, load_balancer: LoadBalancer, registration_service: RegistrationService):
        logger.info("Initializing MeteoService")
        self._load_balancer = load_balancer
        self._registration_service = registration_service

    def send_meteo_data(self, meteo_data: RawMeteoData):
        logger.debug(f"Received meteo data {meteo_data}")
        self._load_balancer.send_meteo_data(meteo_data)

    def send_pollution_data(self, pollution_data: RawPollutionData):
        logger.debug(f"Received pollution data {pollution_data}")
        self._load_balancer.send_pollution_data(pollution_data)
