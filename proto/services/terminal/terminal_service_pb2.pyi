from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Results(_message.Message):
    __slots__ = ["pollution_data", "wellness_data"]
    POLLUTION_DATA_FIELD_NUMBER: _ClassVar[int]
    WELLNESS_DATA_FIELD_NUMBER: _ClassVar[int]
    pollution_data: float
    wellness_data: float
    def __init__(self, wellness_data: _Optional[float] = ..., pollution_data: _Optional[float] = ...) -> None: ...
