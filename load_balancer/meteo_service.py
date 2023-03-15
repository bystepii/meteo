from load_balancer.load_balancer import LoadBalancer
from load_balancer.registration_service import RegistrationService
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData


class MeteoService:
    def __init__(self, load_balancer: LoadBalancer, registration_service: RegistrationService):
        self._load_balancer = load_balancer
        self._registration_service = registration_service

    def send_meteo_data(self, meteo_data: RawMeteoData):
        pass

    def send_pollution_data(self, pollution_data: RawPollutionData):
        pass
