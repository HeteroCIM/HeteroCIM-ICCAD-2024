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
# print(dram.size)def 
dram = DRAM(name="dram", config_path="test_dram.ini")
global_buffer = Buffer(name = "g_buf", config_path = "test_chip.ini", key = "Global Buffer")
tile1 = Tile(name = "tile1", config_path = "test_tile_1.ini")

def eventDriven():
    ld1 = LoadEvent(event_name = "ld1", event_id = 1, event_dependency = [], event_status = EventStatus.wait, src=dram, dst=tile1.PEs[0], data_size=784*8)
    mm1 = CrossbarMultEvent(event_name = "mm1", event_id = 2, event_dependency = [ld1], event_status = EventStatus.wait, input_1_shape = [1,784], input_2_shape = [784,100], hardware = tile1.PEs[0])
    st1 = StoreEvent(event_name = "st1", event_id = 1, event_dependency = [], event_status = EventStatus.wait, src=tile1.PEs[0], dst=dram, data_size=10*8)
    # event_list = [ld1, mm1, mv1, mm2]
    event_list = [ld1, st1]

    inf_T  = 0
    inf_E = 0
    program_T  = 0
    program_E = 0
    for event in event_list:
        dict_detail = {}
        print(event.event_name)
        T, E, stats = executeEvent(event)
        inf_T += T
        inf_E += E
        print(stats)
        print("event:",event.event_name,"latency:", T,"energy", E)
    print("inf_T:", inf_T, "inf_E:", inf_E)
    # print("##################################################################")

    print("program_T:", program_T, "program_E:", program_E)
    total_T = inf_T + program_T
    total_E = inf_E + program_E
    print("total_T:", total_T, "total_E:", total_E)

def get_area():
    area_stats = {}
    tile_1_area_stats = {}
    tile_1_area = tile1.getArea(tile_1_area_stats)
    global_buffer_area = global_buffer.getArea()
    area_stats["area_tile_1"] = tile_1_area
    area_stats["area_global_buffer"] = global_buffer_area

    # total_area = 0
    # for value in area_stats.values():
    #     total_area += value
    total_area = tile_1_area + global_buffer_area
    print("total_area:", total_area, "tile_1_area:", tile_1_area, "global_buffer_area", global_buffer_area)
    print("--------------detailed stats------------------")
    print("tile_1_area_stats\n",tile_1_area_stats)

eventDriven()
# get_area()