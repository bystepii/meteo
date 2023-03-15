from google.protobuf.empty_pb2 import Empty

from load_balancer.registration_service import RegistrationService
from proto.services.registration import registration_service_pb2_grpc
from proto.services.registration.registration_service_pb2 import Address, RegisterResponse


class RegistrationServiceServicer(registration_service_pb2_grpc.RegistrationServiceServicer):
    def __init__(self, registration_service: RegistrationService):
        self._registration_service = registration_service

    def Register(self, address: Address, context) -> RegisterResponse:
        response = RegisterResponse()
        response.success = self._registration_service.register(address.address)
        return response

    def Unregister(self, address: Address, context) -> Empty:
        self._registration_service.unregister(address.address)
        return Empty()
