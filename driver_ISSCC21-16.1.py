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
tile_1 = Tile(name = "tile_1", config_path = "config_files/ISSCC21-16.1_tile_8b.ini")
tile_2 = Tile(name = "tile_2", config_path = "config_files/ISSCC21-16.1_tile_4b.ini")
tile_3 = Tile(name = "tile_3", config_path = "config_files/ISSCC21-16.1_tile_2b.ini")

def eventDriven():
    mm1 = VecMatMulEvent(event_name = "mm1", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,128], hardware = tile_1)
    mm2 = VecMatMulEvent(event_name = "mm2", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,256], hardware = tile_2)
    mm3 = VecMatMulEvent(event_name = "mm3", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,512], hardware = tile_3)
    event_list = [mm1, mm2, mm3]

    inf_T  = 0
    inf_E = 0
    program_T  = 0
    program_E = 0
    event_PP_dict = {}
    for event in event_list:
        dict_detail = {}
        # print(event.event_name)
        T, E, stats = executeEvent(event)
        inf_T += T
        inf_E += E
        print(event.event_name + ":")
        print(stats)
        print("event:",event.event_name,"latency:", T,"energy", E)
        event_PP_dict[event] = [T, E]
    print("inf_T:", inf_T, "inf_E:", inf_E)
    # # print("##################################################################")
    # for event in wmem_event_list:
    #     dict_detail = {}
    #     T, E, stats = executeEvent(event)
    #     program_T += T
    #     program_E += E
    #     # print(event.event_name + ":")
    #     # print(stats)
    #     # print("event:",event.event_name,"latency:", T,"energy", E)
    # print("program_T:", program_T, "program_E:", program_E)
    # total_T = inf_T + program_T
    # total_E = inf_E + program_E
    # print("total_T:", total_T, "total_E:", total_E)

def get_area():
    area_stats = {}
    tile_1_area_stats = {}
    tile_2_area_stats = {}
    tile_3_area_stats = {}
    tile_4_area_stats = {}
    tile_1_area = tile_1.getArea(tile_1_area_stats)
    area_stats["area_tile_1"] = tile_1_area

    # total_area = 0
    # for value in area_stats.values():
    #     total_area += value
    total_area = tile_1_area
    print("total_area:", total_area, "tile_1_area:", tile_1_area)
    print("--------------detailed stats------------------")
    print("tile_1_area_stats\n",tile_1_area_stats)
eventDriven()
get_area()