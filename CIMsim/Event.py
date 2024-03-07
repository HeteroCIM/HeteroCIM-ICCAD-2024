from enum import Enum
from typing import List, Optional
from CIMsim.Tile import *
class EventType(Enum):
    MatmulEvent = 0
    ReluEvent = 1
    LoadEvent = 2
    StoreEvent = 3
    MoveEvent = 4
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

class MatmulEvent(BaseEvent):
    def __init__(self, event_name: str, event_id: int, event_dependency: List[BaseEvent], event_status: EventStatus, input_1_shape: List[int], input_2_shape: List[int], assigned_hardware):
        super().__init__(event_name, EventType.MatmulEvent, event_id, event_dependency, event_status)
        self.input_1_shape = input_1_shape
        self.input_2_shape = input_2_shape
        assert self.input_1_shape[1] == self.input_2_shape[0], "Error creating MatmulEvent: matrix shape does not match"
        self.assigned_hardware = assigned_hardware 

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