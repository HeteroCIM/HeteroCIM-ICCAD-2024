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

ps = Parser(tile_config_path = "test_tile_1.ini", DRAM_config_path = "test_dram.ini", CGRA_config_path ="test_fpga.ini" )
ps.tile_NVM_config_path = "/home/siyuan/HeteroCIM1.0/test_on_tile_nvm.ini"
eventlist = ps.parse_linecode_file("/home/siyuan/HeteroCIM1.0/examples/linecode_move.json")
# eventlist = ps.parse_linecode_file("examples/test.json")
for event in eventlist:
    print(event_to_string(event))

    # print("event:", event.event_name, "latency:", event_T, "energy", event_E)

ex = eventExecuter()
res_dict = ex.execute_events(eventlist)
for event in eventlist:
    res_tuple = res_dict[event]
    event_T = res_tuple[0]
    event_E = res_tuple[1]
    stats = res_tuple[2]
    print("event:", event.event_name, "latency:", event_T, "energy", event_E)