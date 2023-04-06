from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Results(_message.Message):
    __slots__ = ["pollution_data", "pollution_timestamp", "wellness_data", "wellness_timestamp"]
    POLLUTION_DATA_FIELD_NUMBER: _ClassVar[int]
    POLLUTION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WELLNESS_DATA_FIELD_NUMBER: _ClassVar[int]
    WELLNESS_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    pollution_data: float
    pollution_timestamp: _timestamp_pb2.Timestamp
    wellness_data: float
    wellness_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, wellness_data: _Optional[float] = ..., wellness_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., pollution_data: _Optional[float] = ..., pollution_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
