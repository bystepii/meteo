import logging

from google.protobuf.empty_pb2 import Empty

from common.registration_service import RegistrationService
from proto.services.registration import registration_service_pb2_grpc
from proto.services.registration.registration_service_pb2 import Address, RegisterResponse

logger = logging.getLogger(__name__)


class RegistrationServiceServicer(registration_service_pb2_grpc.RegistrationServiceServicer):
    def __init__(self, registration_service: RegistrationService):
        logger.info("Initializing RegistrationServiceServicer")
        self._registration_service = registration_service

    def Register(self, address: Address, context) -> RegisterResponse:
        logger.debug(f"Received registration request for {address.address}")
        response = RegisterResponse()
        response.success = self._registration_service.register(address.address)
        return response

    def Unregister(self, address: Address, context) -> Empty:
        logger.debug(f"Received unregistration request for {address.address}")
        self._registration_service.unregister(address.address)
        return Empty()
