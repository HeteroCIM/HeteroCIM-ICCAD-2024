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

class Simulator():
    def __init__(self, tile_config_path = "", DRAM_config_path = "", FPGA_config_path = "", protocol_config_path = "", nvm_config_path = ""):
        self.tile_config_path = tile_config_path
        self.DRAM_config_path = DRAM_config_path
        self.FPGA_config_path = FPGA_config_path
        self.protocol_config_path = protocol_config_path
        self.nvm_config_path = nvm_config_path

    def parse_json(self, filename):
        ps = Parser(self.tile_config_path, self.DRAM_config_path, self.FPGA_config_path)
        ps.tile_NVM_config_path = self.nvm_config_path
        self.event_list = ps.parse_linecode_file(filename)
        for event in event_list:
            print(event_to_string(event))
    
    def execute_event(self):
        ex = eventExecuter()
        self.res_dict = ex.execute_events(self.event_list)
        for event in self.event_list:
            res_tuple = self.res_dict[event]
            event_T = res_tuple[0]
            event_E = res_tuple[1]
            stats = res_tuple[2]
            print("event:", event.event_name, "latency:", event_T, "energy", event_E)


sim = Simulator(tile_config_path = "test_tile_1.ini", DRAM_config_path = "test_dram.ini", FPGA_config_path ="test_fpga.ini", protocol_config_path = "test_Noc.ini")