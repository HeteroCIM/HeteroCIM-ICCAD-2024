import configparser as cp
from CIMsim.utils import *
# NVM means nonlinear vector module. NVM is responsible for nonlinear operations and SIMD vector operations

def cal_LUT_cost(LUT_size):
    latency = 1
    energy = 1
    return latency, energy

class GeLU():
    def __init__(self, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.use_LUT = config.getboolean("GeLU", "use_LUT")
        self.precision = config.getint("GeLU", "precision") # e.g. 8bit
        self.LUT_size = -1
        if self.use_LUT:
            self.LUT_size = config.getint("GeLU", "LUT_size_" + str(self.precision))




class NVM():
    def __init__(self, name, config_path = ""):
        # default: bandwidth 19.2GB/s (DDR4) 
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.size = config.getfloat("NVM", "size")
        self.energy_per_bit = config.getfloat("NVM", "energy_per_bit")
        self.bit_width = config.getint("NVM", "bit_width")
        self.read_access_latency = config.getfloat("NVM", "read_access_latency")
        self.write_access_latency = config.getfloat("NVM", "write_access_latency")
        self.dram_frequency = config.getfloat("NVM", "dram_frequency")
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