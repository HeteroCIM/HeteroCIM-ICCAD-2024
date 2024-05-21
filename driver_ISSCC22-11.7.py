import os
from HeteroCIM.DRAM import *
from HeteroCIM.Crossbar import *
from HeteroCIM.Event import *
from HeteroCIM.Tile import *
from HeteroCIM.Buffer import *
from HeteroCIM.EventExecutor import *
from HeteroCIM.NonlinearVecModule import *
# crossbar = Crossbar("config.ini")
# print(crossbar.compute(64,64))

# dram = DRAM("config.ini")
# print(dram.size)def 
tile_1 = Tile(name = "tile_1", config_path = "ISSCC22-11.7.ini")

def eventDriven():
    mm1 = CrossbarMultEvent(event_name = "mm1", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1, 256], input_2_shape = [256,64], hardware = tile_1.PEs[0])
    event_list = [mm1]

    inf_T  = 0
    inf_E = 0
    program_T  = 0
    program_E = 0
    event_PP_dict = {}
    for event in event_list:
        dict_detail = {}
        # print(event.event_name)
        ex = eventExecuter()
        T, E, stats = ex.execute_event(event)
        inf_T += T
        inf_E += E
        print(event.event_name + ":")
        print(stats)
        print("event:",event.event_name,"latency:", T,"energy", E)
        event_PP_dict[event] = [T, E]
    print("inf_T:", inf_T, "inf_E:", inf_E)

eventDriven()