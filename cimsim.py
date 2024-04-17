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

sim = Simulator(tile_config_path = "test_tile_1.ini", DRAM_config_path = "test_dram.ini", FPGA_config_path ="test_fpga.ini", protocol_config_path = "test_Noc.ini", nvm_config_path = "test_on_tile_nvm.ini")
sim.add_protocol()
# sim.parse_json("/home/siyuan/CIMsim_Plus/examples/test.json")
sim.parse_json("/home/siyuan/CIMsim_Plus/examples/linecode_bert_block.json")
sim.print_event_list("event.txt")
sim.execute_event()
sim.print_simulation_result("event_res.txt")
sim.parser_stats_dict = sim.get_stats_from_res(sim.parser_res_dict)
print("raw stats after parser:")
sim.print_stats(sim.parser_stats_dict)
sim.schedule()
sim.print_simulation_result("schedule_res.txt")