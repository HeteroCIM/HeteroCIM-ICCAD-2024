import configparser as cp
class DRAM():
    def __init__(self, name, config_path = ""):
        # default: bandwidth 19.2GB/s (DDR4) 
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        # self.bandwidth = config.getfloat("DRAM", "bandwidth")
        self.size = config.getfloat("DRAM", "size")
        self.energy_per_bit = config.getfloat("DRAM", "energy_per_bit")
        self.bit_width = config.getint("DRAM", "bit_width")
        self.access_latency = config.getfloat("DRAM", "access_latency")
        self.dram_frequency = config.getfloat("DRAM", "dram_frequency")
    def read(self, data_size, true_data=False):
        # data_size: bit
        if ~true_data:
            # cycles / frequency
            latency = (self.access_latency + data_size / self.bit_width) / self.dram_frequency
            energy = self.energy_per_bit * data_size
            return latency, energy
