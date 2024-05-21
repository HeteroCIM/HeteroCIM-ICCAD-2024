import os
from HeteroCIM.DRAM import *
from HeteroCIM.Crossbar import *
from HeteroCIM.Event import *
from HeteroCIM.Tile import *
from HeteroCIM.Buffer import *
from HeteroCIM.EventExecutor import *
from HeteroCIM.NonlinearVecModule import *
from HeteroCIM.Parser import *
from HeteroCIM.utils import *
from HeteroCIM.Simulator import *
import time
t1 = time.time()
sim = Simulator(tile_config_path = "system_config_files/tile.ini", DRAM_config_path = "system_config_files/dram.ini", CGRA_config_path ="system_config_files/fpga.ini", protocol_config_path = "system_config_files/inter_die_connection.ini", nvm_config_path = "system_config_files/on_tile_nvm.ini")
sim.build_inter_die_protocol()
# sim.parse_json("/home/siyuan/HeteroCIM1.0/examples/linecode_vgg16.json")
# sim.parse_json("/home/siyuan/HeteroCIM1.0/examples/linecode_bert_block.json")
sim.parse_json("/home/siyuan/HeteroCIM1.0/examples/linecode_bert_small.json")
sim.print_event_list("outputs/event.txt")
# t1 = time.time()
sim.execute_event()
t2 = time.time()
sim.print_event_T_E("outputs/raw_events.txt")
sim.parser_stats_dict = sim.get_raw_layer_T_E(sim.event_T_E_dict)
t3 = time.time()
sim.schedule()
print("stats after scheduling:")
sim.print_layer_T_E(sim.sched_layer_T_E_dict)
t4 = time.time()
sim.print_event_T_E("outputs/sched_events.txt")
t5 = time.time()
sim.get_CIM_tile_area()
t6 = time.time()
print("execution time: ", t2-t1)
print("scheduling time: ", t4-t3)
print("area time: ", t6-t5)