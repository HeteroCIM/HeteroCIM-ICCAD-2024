import os
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.Tile import *
from CIMsim.Buffer import *
from CIMsim.EventExecutor import *
from CIMsim.NonlinearVecModule import *
from CIMsim.Parser import *
from CIMsim.utils import *
from CIMsim.Simulator import *
import time
t1 = time.time()
sim = Simulator(tile_config_path = "test_tile_1.ini", DRAM_config_path = "test_dram.ini", FPGA_config_path ="test_fpga.ini", protocol_config_path = "test_Noc.ini", nvm_config_path = "test_on_tile_nvm.ini")
sim.build_inter_die_protocol()
# sim.parse_json("/home/siyuan/CIMsim_Plus/examples/linecode_vgg16.json")
# sim.parse_json("/home/siyuan/CIMsim_Plus/examples/linecode_bert_block.json")
sim.parse_json("/home/siyuan/CIMsim_Plus/examples/linecode_bert_small.json")
sim.print_event_list("event.txt")
# t1 = time.time()
sim.execute_event()
t2 = time.time()
sim.print_event_T_E("raw_events.txt")
sim.parser_stats_dict = sim.get_raw_layer_T_E(sim.event_T_E_dict)
t3 = time.time()
sim.schedule()
print("stats after scheduling:")
sim.print_layer_T_E(sim.sched_layer_T_E_dict)
t4 = time.time()
sim.print_event_T_E("sched_events.txt")
t5 = time.time()
sim.get_CIM_tile_area()
t6 = time.time()
print("execution time: ", t2-t1)
print("scheduling time: ", t4-t3)
print("area time: ", t6-t5)