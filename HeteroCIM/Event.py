from enum import Enum
from typing import List, Optional
from HeteroCIM.Tile import *
class EventType(Enum):
    CrossbarMultEvent = 0
    ReluEvent = 1
    LoadEvent = 2
    StoreEvent = 3
    MoveEvent = 4
    CrossbarWriteEvent = 5
    ActivationEvent = 6
    VectorEvent = 7
    ReduceEvent = 8
    CGRABatMatmulEvent = 9
    MergeEvent = 10
    BarrierEvent = 11
class MergeEventType(Enum):
    MergeAdd = 0 
class VectorEventType(Enum):
    VectorReLU = 0 
    VectorAdd = 1
    VectorSub = 2
    VectorMul = 3
    VectorDiv = 4
    VectorMax = 5
    VectorMin = 6
    VectorExp = 7
    VectorSqrt = 8
    VectorPReLU = 10
    VectorGeLU = 11
    VectorSigmoid = 12
    VectorTanh = 13
    VectorELU = 14
    VectorSiLU = 15
class ReduceEventType(Enum):
    Softmax = 0
    Layernorm = 1
class EventStatus(Enum):
    wait = 0
    process = 1
    complete = 2

def vector_event_type_to_string(vector_event_type):
    vector_event_type_to_string_dict = {
        VectorEventType.VectorReLU: "VectorReLU",
        VectorEventType.VectorAdd: "VectorAdd",
        VectorEventType.VectorSub: "VectorSub",
        VectorEventType.VectorMul: "VectorMul",
        VectorEventType.VectorDiv: "VectorDiv",
        VectorEventType.VectorMax: "VectorMax",
        VectorEventType.VectorMin: "VectorMin",
        VectorEventType.VectorExp: "VectorExp",
        VectorEventType.VectorSqrt: "VectorSqrt",
        VectorEventType.VectorPReLU: "VectorPReLU",
        VectorEventType.VectorGeLU: "VectorGeLU",
        VectorEventType.VectorSigmoid: "VectorSigmoid",
        VectorEventType.VectorTanh: "VectorTanh",
        VectorEventType.VectorELU: "VectorELU",
        VectorEventType.VectorSiLU: "VectorSiLU"
    }
    return vector_event_type_to_string_dict[vector_event_type]

_event_type_to_string_dict = {
    EventType.CrossbarMultEvent: "CrossbarMultEvent",
    EventType.LoadEvent: "LoadEvent",
    EventType.StoreEvent: "StoreEvent",
    EventType.MoveEvent: "MoveEvent",
    EventType.CrossbarWriteEvent: "CrossbarWriteEvent",
    EventType.ActivationEvent: "ActivationEvent",
    EventType.VectorEvent: "VectorEvent",
    EventType.ReduceEvent: "ReduceEvent",
    EventType.CGRABatMatmulEvent: "CGRABatMatmulEvent",
    EventType.MergeEvent: "MergeEvent",
    EventType.BarrierEvent: "BarrierEvent"
}

def reduce_event_type_to_string(reduce_event_type):
    reduce_event_type_to_string_dict = {
        ReduceEventType.Softmax: "ReduceSoftmax",
        ReduceEventType.Layernorm: "ReduceLayernorm",
    }
    return reduce_event_type_to_string_dict[reduce_event_type]

class BaseEvent(object):
    def __init__(self, event_name: str, event_type: EventType, event_id: int, event_dependency: List, event_status: EventStatus):
        self.event_name = event_name
        self.event_type = event_type
        self.event_id = event_id
        self.event_dependency = event_dependency
        self.event_status = event_status
        self.attr = {}
    def set_attr(self, attr_name, attr_value):
        self.attr[attr_name] = attr_value
    def get_attr(self, attr_name):
        return self.attr[attr_name]
    def has_attr(self, attr_name):
        if attr_name in self.attr.keys():
            return True
        else:
            return False
    def to_string(self):
        type_str = _event_type_to_string_dict[self.event_type]
        id_str = self.event_id
        name_str = self.event_name
        event_str = "event_id: " + str(id_str) + "  event_name: " + name_str + "  event_type: " + type_str
        return event_str


class CrossbarMultEvent(BaseEvent):
    def __init__(self, event_name: str, event_id: int, event_dependency: List[BaseEvent], event_status: EventStatus, input_1_shape: List[int], input_2_shape: List[int], hardware):
        super().__init__(event_name, EventType.CrossbarMultEvent, event_id, event_dependency, event_status)
        self.input_1_shape = input_1_shape # 1*m
        self.input_2_shape = input_2_shape # m*n
        assert self.input_1_shape[1] == self.input_2_shape[0], "Error creating CrossbarMultEvent: matrix shape does not match"
        self.hardware = hardware 

class LoadEvent(BaseEvent):
    # load from DRAM
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, src, dst, size: int, data_bits: int):
        super().__init__(event_name, EventType.LoadEvent, event_id, event_dependency, event_status)
        self.src = src
        self.dst = dst
        self.size = size
        self.data_bits = data_bits

class StoreEvent(BaseEvent):
    # store to DRAM
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, src, dst, size: int, data_bits: int):
        super().__init__(event_name, EventType.StoreEvent, event_id, event_dependency, event_status)
        self.src = src
        self.dst = dst
        self.size = size
        self.data_bits = data_bits

class MoveEvent(BaseEvent):
    # move between buffer/regs
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, src, dst, size: int, data_bits: int):
        super().__init__(event_name, EventType.MoveEvent, event_id, event_dependency, event_status)
        self.src = src
        self.dst = dst
        self.size = size
        self.data_bits = data_bits

class CrossbarWriteEvent(BaseEvent):
    # write weight into crossbar
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, n_rows: int, n_cols: int, hardware: PE, data_bits: int):
        super().__init__(event_name, EventType.CrossbarWriteEvent, event_id, event_dependency, event_status)
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.hardware = hardware
        self.data_bits = data_bits

class ActivationEvent(BaseEvent):
    # elementwise activation, executed in the vector module. 
    # Note: ReLU function may be fused with conv or fc and executed in the tile
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, input_shape: List[int], activation_name: str, hardware, data_bits: int):
        super().__init__(event_name, EventType.ActivationEvent, event_id, event_dependency, event_status)
        self.input_shape = input_shape
        self.hardware = hardware
        self.activation_name = activation_name
        self.data_bits = data_bits

class VectorEvent(BaseEvent):
    # executed in the vector module
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, vec_type: VectorEventType, input_1_size, input_2_size, hardware, data_bits: int):
        super().__init__(event_name, EventType.VectorEvent, event_id, event_dependency, event_status)
        self.vec_type = vec_type
        self.input_1_size = input_1_size
        self.input_2_size = input_2_size
        self.data_bits = data_bits
        self.hardware = hardware

class ReduceEvent(BaseEvent):
    # executed in the vector module
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, reduce_type: ReduceEventType, input_1_size, input_2_size, hardware, data_bits: int):
        super().__init__(event_name, EventType.ReduceEvent, event_id, event_dependency, event_status)
        self.reduce_type = reduce_type
        self.input_1_size = input_1_size
        self.input_2_size = input_2_size
        self.data_bits = data_bits
        self.hardware = hardware

class CGRABatMatmulEvent(BaseEvent):
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, B: int, M: int, N: int, P: int, hardware, data_bits: int):
        super().__init__(event_name, EventType.CGRABatMatmulEvent, event_id, event_dependency, event_status)
        self.B = B
        self.M = M
        self.N = N
        self.P = P
        self.data_bits = data_bits
        self.hardware = hardware

class MergeEvent(BaseEvent):
    # executed in the vector module
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, merge_type, input_1_size, input_2_size, hardware, data_bits: int):
        super().__init__(event_name, EventType.MergeEvent, event_id, event_dependency, event_status)
        self.input_1_size = input_1_size
        self.input_2_size = input_2_size
        self.merge_type = merge_type
        self.data_bits = data_bits
        self.hardware = hardware