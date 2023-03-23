import logging

from google.protobuf.empty_pb2 import Empty
from grpc import ServicerContext

from common.registration_service import RegistrationService, Address
from proto.services.registration import registration_service_pb2_grpc
from proto.services.registration.registration_service_pb2 import RegisterRequest, RegisterResponse, UID

logger = logging.getLogger(__name__)


class RegistrationServiceServicer(registration_service_pb2_grpc.RegistrationServiceServicer):
    def __init__(self, registration_service: RegistrationService):
        logger.info("Initializing RegistrationServiceServicer")
        self._registration_service = registration_service

    def Register(self, req: RegisterRequest, context: ServicerContext) -> RegisterResponse:
        proto, ip, port = context.peer().split(":")
        logger.debug(f"Received register request for \"{req.address}:{req.port}\" from {context.peer()}")
        addr = req.address or ip
        response = RegisterResponse()
        response.success = self._registration_service.register(req.uid, Address(address=addr, port=req.port))
        return response

    def Unregister(self, uid: UID, context: ServicerContext) -> Empty:
        logger.debug(f"Received unregister request for {uid.uid} from {context.peer()}")
        self._registration_service.unregister(uid.uid)
        return Empty()
