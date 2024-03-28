import os
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.Tile import *
from CIMsim.Buffer import *
from CIMsim.EventExecutor import *
from CIMsim.NonlinearVecModule import *
# crossbar = Crossbar("config.ini")
# print(crossbar.compute(64,64))

# dram = DRAM("config.ini")
# print(dram.size)

dram = DRAM(name="dram", config_path="system.ini")
global_buffer = Buffer(name = "g_buf", config_path = "chip.ini", key = "Global Buffer")
tile1 = Tile(name = "tile1", config_path = "tile1.ini")
tile2 = Tile(name = "tile2", config_path = "tile2.ini")
nonlinear_vec_module = NonlinearVecModule(name = "nvm", config_path = "nvm.ini")

ld1 = LoadEvent(event_name = "ld1", event_id = 1, event_dependency = [], event_status = EventStatus.wait, src=dram, dst=tile1, data_size=784*8)
mm1 = VecMatMulEvent(event_name = "mm1", event_id = 2, event_dependency = [ld1], event_status = EventStatus.wait, input_1_shape = [1,784], input_2_shape = [784,100], hardware = tile1)
mv1 = MoveEvent(event_name= "mv1", event_id=3, event_dependency = [mm1], event_status=EventStatus.wait, src=tile1, dst=tile2, data_size=100*8)
mm2 = VecMatMulEvent(event_name = "mm2", event_id = 3, event_dependency = [mv1], event_status = EventStatus.wait, input_1_shape = [1,100], input_2_shape = [100,10], hardware = tile2)
gelu1 = ActivationEvent(event_name = "gelu1", event_id = 5, event_dependency = [], event_status = EventStatus.wait, input_shape = [1,100], activation_name = "GeLU", hardware = nonlinear_vec_module)
# event_list = [ld1, mm1, mv1, mm2] 
event_list = [mm1, mm2, gelu1] 
for event in event_list:
    dict_detail = {}
    print(event.event_name)
    T, E, stats = executeEvent(event)
    print(stats)
    print("event:",event.event_name,"latency:", T,"energy", E)
