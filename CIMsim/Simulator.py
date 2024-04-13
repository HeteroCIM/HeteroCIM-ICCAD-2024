import os
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.EventExecutor import *
from CIMsim.Parser import *
from CIMsim.utils import event_to_string

class Simulator():
    def __init__(self, tile_config_path = "", DRAM_config_path = "", FPGA_config_path = "", protocol_config_path = "", nvm_config_path = ""):
        self.tile_config_path = tile_config_path
        self.DRAM_config_path = DRAM_config_path
        self.FPGA_config_path = FPGA_config_path
        self.protocol_config_path = protocol_config_path
        self.nvm_config_path = nvm_config_path
        self.hardware_dict = {}

    def add_protocol(self):
        assert self.protocol_config_path != "", "cannot find protocol config file!"
        config = cp.ConfigParser()
        config.read(self.protocol_config_path)
        if config["Protocol"]["inter_chip_connection"] == "PCIe":
            pcie = PCIe("PCIe", self.protocol_config_path)
            self.hardware_dict["inter_chip_connection"] = pcie
        else:
            assert(0 and "unsupported protocol")

    def parse_json(self, filename):
        ps = Parser(self.tile_config_path, self.DRAM_config_path, self.FPGA_config_path)
        ps.tile_NVM_config_path = self.nvm_config_path
        self.event_list = ps.parse_linecode_file(filename)
        self.hardware_dict.update(ps.get_hardware_dict())
        # for event in self.event_list:
        #     print(event_to_string(event))
        for hardware_name in self.hardware_dict.keys():
            print(self.hardware_dict[hardware_name].name)
    
    def execute_event(self):
        ex = eventExecuter(self.hardware_dict)
        self.res_dict = ex.execute_events(self.event_list)
        for event in self.event_list:
            res_tuple = self.res_dict[event]
            event_T = res_tuple[0]
            event_E = res_tuple[1]
            stats = res_tuple[2]
            print("event:", event.event_name, "latency:", event_T, "energy", event_E)