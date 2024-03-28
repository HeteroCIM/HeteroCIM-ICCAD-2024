from enum import Enum
from typing import List, Optional
from CIMsim.Tile import *
class EventType(Enum):
    VecMatMulEvent = 0
    ReluEvent = 1
    LoadEvent = 2
    StoreEvent = 3
    MoveEvent = 4
    WriteEvent = 5
    ActivationEvent = 6
    VectorEvent = 7
    ReduceEvent = 8
class VectorEventType(Enum):
    ReLUEvent = 0 
    AddEvent = 1 # can be used for bias
class EventStatus(Enum):
    wait = 0
    process = 1
    complete = 2

class BaseEvent(object):
    def __init__(self, event_name: str, event_type: EventType, event_id: int, event_dependency: List, event_status: EventStatus):
        self.event_name = event_name
        self.event_type = event_type
        self.event_id = event_id
        self.event_dependency = event_dependency
        self.event_status = event_status

class VecMatMulEvent(BaseEvent):
    def __init__(self, event_name: str, event_id: int, event_dependency: List[BaseEvent], event_status: EventStatus, input_1_shape: List[int], input_2_shape: List[int], hardware):
        super().__init__(event_name, EventType.VecMatMulEvent, event_id, event_dependency, event_status)
        self.input_1_shape = input_1_shape # 1*m
        self.input_2_shape = input_2_shape # m*n
        assert self.input_1_shape[1] == self.input_2_shape[0], "Error creating VecMatMulEvent: matrix shape does not match"
        self.hardware = hardware 

class LoadEvent(BaseEvent):
    # load from DRAM
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, src, dst, data_size: int):
        super().__init__(event_name, EventType.LoadEvent, event_id, event_dependency, event_status)
        self.src = src
        self.dst = dst
        self.data_size = data_size

class StoreEvent(BaseEvent):
    # store to DRAM
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, src, dst, data_size: int):
        super().__init__(event_name, EventType.StoreEvent, event_id, event_dependency, event_status)
        self.src = src
        self.dst = dst
        self.data_size = data_size

class MoveEvent(BaseEvent):
    # move between buffer/regs
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, src, dst, data_size: int):
        super().__init__(event_name, EventType.MoveEvent, event_id, event_dependency, event_status)
        self.src = src
        self.dst = dst
        self.data_size = data_size

class WriteEvent(BaseEvent):
    # write weight into crossbar
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, n_rows: int, n_cols: int, tile: Tile):
        super().__init__(event_name, EventType.WriteEvent, event_id, event_dependency, event_status)
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.tile = tile

class ActivationEvent(BaseEvent):
    # elementwise activation, executed in the vector module. 
    # Note: ReLU function may be fused with conv or fc and executed in the tile
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, input_shape: List[int], activation_name: str, hardware):
        super().__init__(event_name, EventType.ActivationEvent, event_id, event_dependency, event_status)
        self.input_shape = input_shape
        self.hardware = hardware
        self.activation_name = activation_name

class VectorEvent(BaseEvent):
    # executed in the vector module
    def __init__(self, event_name: str, event_id: int, event_dependency: List, event_status: EventStatus, vec_type: VectorEventType, input_1_size = None, input_2_size = None,):
        super().__init__(event_name, EventType.VectorEvent, event_id, event_dependency, event_status)
        self.vec_type = vec_type
        self.input_1_size = input_1_size
        self.input_2_size = input_2_size