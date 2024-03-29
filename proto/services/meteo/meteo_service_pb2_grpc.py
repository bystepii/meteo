# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from proto.messages.meteo import meteo_messages_pb2 as proto_dot_messages_dot_meteo_dot_meteo__messages__pb2


class MeteoServiceStub(object):
    """MeteoService is used to send meteorological data to the server
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendMeteoData = channel.unary_unary(
                '/meteo.MeteoService/SendMeteoData',
                request_serializer=proto_dot_messages_dot_meteo_dot_meteo__messages__pb2.RawMeteoData.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.SendPollutionData = channel.unary_unary(
                '/meteo.MeteoService/SendPollutionData',
                request_serializer=proto_dot_messages_dot_meteo_dot_meteo__messages__pb2.RawPollutionData.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class MeteoServiceServicer(object):
    """MeteoService is used to send meteorological data to the server
    """

    def SendMeteoData(self, request, context):
        """Send meteorological data to the server
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendPollutionData(self, request, context):
        """Send pollution data to the server
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MeteoServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendMeteoData': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMeteoData,
                    request_deserializer=proto_dot_messages_dot_meteo_dot_meteo__messages__pb2.RawMeteoData.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'SendPollutionData': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPollutionData,
                    request_deserializer=proto_dot_messages_dot_meteo_dot_meteo__messages__pb2.RawPollutionData.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'meteo.MeteoService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MeteoService(object):
    """MeteoService is used to send meteorological data to the server
    """

    @staticmethod
    def SendMeteoData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/meteo.MeteoService/SendMeteoData',
            proto_dot_messages_dot_meteo_dot_meteo__messages__pb2.RawMeteoData.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendPollutionData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/meteo.MeteoService/SendPollutionData',
            proto_dot_messages_dot_meteo_dot_meteo__messages__pb2.RawPollutionData.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
