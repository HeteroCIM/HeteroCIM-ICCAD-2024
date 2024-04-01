import configparser as cp
from CIMsim.utils import *
class DRAM():
    def __init__(self, name, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        # self.bandwidth = config.getfloat("DRAM", "bandwidth")
        self.size = config.getfloat("DRAM", "size")
        self.energy_per_bit = config.getfloat("DRAM", "energy_per_bit")
        self.bit_width = config.getint("DRAM", "bit_width")
        self.read_access_latency = config.getfloat("DRAM", "read_access_latency")
        self.write_access_latency = config.getfloat("DRAM", "write_access_latency")
        self.dram_frequency = config.getfloat("DRAM", "dram_frequency")
        self.name = name
    def read(self, data_size, stats = {}, true_data=False):
        # data_size: bit
        if ~true_data:
            # cycles / frequency
            latency = (self.read_access_latency + data_size / self.bit_width) / self.dram_frequency
            energy = self.energy_per_bit * data_size
            local_stats = {}
            local_stats[self.name + "_dram_r_T"] = latency
            local_stats[self.name + "_dram_r_E"] = energy
            merge_stats_add(stats, local_stats)
            return latency, energy
    def write(self, data_size, stats = {}, true_data=False):
        # data_size: bit
        if ~true_data:
            # cycles / frequency
            latency = (self.write_access_latency + data_size / self.bit_width) / self.dram_frequency
            energy = self.energy_per_bit * data_size
            local_stats = {}
            local_stats[self.name + "_dram_w_T"] = latency
            local_stats[self.name + "_dram_w_E"] = energy
            merge_stats_add(stats, local_stats)
            return latency, energy
