# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from proto.services.registration import registration_service_pb2 as proto_dot_services_dot_registration_dot_registration__service__pb2


class RegistrationServiceStub(object):
    """RegistrationService is used to register and unregister servers and/or terminals
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/registration.RegistrationService/Register',
                request_serializer=proto_dot_services_dot_registration_dot_registration__service__pb2.RegisterRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.Unregister = channel.unary_unary(
                '/registration.RegistrationService/Unregister',
                request_serializer=proto_dot_services_dot_registration_dot_registration__service__pb2.UID.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class RegistrationServiceServicer(object):
    """RegistrationService is used to register and unregister servers and/or terminals
    """

    def Register(self, request, context):
        """Register a server or terminal
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Unregister(self, request, context):
        """Unregister a server or terminal
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RegistrationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=proto_dot_services_dot_registration_dot_registration__service__pb2.RegisterRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Unregister': grpc.unary_unary_rpc_method_handler(
                    servicer.Unregister,
                    request_deserializer=proto_dot_services_dot_registration_dot_registration__service__pb2.UID.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'registration.RegistrationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RegistrationService(object):
    """RegistrationService is used to register and unregister servers and/or terminals
    """

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/registration.RegistrationService/Register',
            proto_dot_services_dot_registration_dot_registration__service__pb2.RegisterRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Unregister(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/registration.RegistrationService/Unregister',
            proto_dot_services_dot_registration_dot_registration__service__pb2.UID.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
