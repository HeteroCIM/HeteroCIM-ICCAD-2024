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
tile1 = Tile(name = "tile_1", config_path = "config_files/Nature23IBM_tile_PWM.ini")
tile2 = Tile(name = "tile_2", config_path = "config_files/Nature23IBM_tile.ini")
tile3 = Tile(name = "tile_3", config_path = "config_files/Nature23IBM_tile.ini")
tile4 = Tile(name = "tile_4", config_path = "config_files/Nature23IBM_tile.ini")

def eventDriven():
    mm1 = VecMatMulEvent(event_name = "mm1", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,512], hardware = tile1)
    mm2 = VecMatMulEvent(event_name = "mm2", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,512], hardware = tile2)
    # mv1 = MoveEvent(event_name= "mv1", event_id=3, event_dependency = [], event_status=EventStatus.wait, src=tile1, dst=tile3, data_size=512*8)
    # mv2 = MoveEvent(event_name= "mv2", event_id=3, event_dependency = [], event_status=EventStatus.wait, src=tile2, dst=tile3, data_size=512*8)
    mm3 = VecMatMulEvent(event_name = "mm3", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,512], hardware = tile3)
    # mv3 = MoveEvent(event_name= "mv3", event_id=3, event_dependency = [], event_status=EventStatus.wait, src=tile3, dst=tile4, data_size=512*8)
    mm4 = VecMatMulEvent(event_name = "mm4", event_id = 2, event_dependency = [], event_status = EventStatus.wait, input_1_shape = [1,512], input_2_shape = [512,12], hardware = tile4)
    # event_list = [mm1, mm2, mv1, mv2, mm3, mv3, mm4]
    event_list = [mm1, mm2, mm3, mm4]



    inf_T  = 0
    inf_E = 0
    program_T  = 0
    program_E = 0
    for event in event_list:
        dict_detail = {}
        # print(event.event_name)
        T, E, stats = executeEvent(event)
        inf_T += T
        inf_E += E
        print(event.event_name + ":")
        print(stats)
        print("event:",event.event_name,"latency:", T,"energy", E)
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
    nvm_area_stats = {}
    tile_1_area = tile1.getArea(tile_1_area_stats)
    tile_2_area = tile2.getArea(tile_2_area_stats)
    global_buffer_area = global_buffer.getArea()
    nvm_module_area = nonlinear_vec_module.getArea(stats = nvm_area_stats)
    area_stats["area_tile_1"] = tile_1_area
    area_stats["area_tile_2"] = tile_2_area
    area_stats["area_global_buffer"] = global_buffer_area
    area_stats["area_nvm_module"] = nvm_module_area

    # total_area = 0
    # for value in area_stats.values():
    #     total_area += value
    total_area = tile_1_area + tile_2_area + nvm_module_area - tile_1_area_stats["tile_1_o_buf_area"]
    print("total_area:", total_area, "tile_1_area:", tile_1_area, "tile_2_area:", tile_2_area, "global_buffer_area", global_buffer_area, "nvm_module_area", nvm_module_area)
    print("--------------detailed stats------------------")
    print("tile_1_area_stats\n",tile_1_area_stats)
    print("tile_2_area_stats\n",tile_2_area_stats)
    print("nvm_area_stats\n",nvm_area_stats)
    stat_dict, ratio_dict = get_detailed_stats(total_area, [tile_1_area_stats, tile_2_area_stats], ["tile_1", "tile_2"], ["i_buf_area", "o_buf_area", "dac_area", "adc_area", "mac_area", "crossbar_area"])
    print(stat_dict)
    print(ratio_dict)

eventDriven()
# get_area()