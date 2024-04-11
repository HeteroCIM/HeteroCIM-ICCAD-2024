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

ps = Parser(tile_config_path = "test_tile_1.ini", DRAM_config_path = "test_dram.ini", FPGA_config_path ="test_fpga.ini" )
ps.tile_NVM_config_path = "/home/siyuan/CIMsim_Plus/test_on_tile_nvm.ini"
eventlist = ps.parse_linecode_file("/home/siyuan/CIMsim_Plus/examples/linecode_bert_block.json")
# eventlist = ps.parse_linecode_file("examples/test.json")
for event in eventlist:
    print(event_to_string(event))