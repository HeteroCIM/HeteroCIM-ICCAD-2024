import configparser as cp
class DRAM():
    def __init__(self, config_path = ""):
        # default: bandwidth 19.2GB/s (DDR4) 
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.bandwidth = config.getfloat("DRAM", "bandwidth")
        self.size = config.getfloat("DRAM", "size")
        self.power = config.getfloat("DRAM", "power")
    def read(self, data_size, true_data=False):
        # data_size: bit
        if ~true_data:
            latency = data_size / self.bandwidth
            energy = latency * self.power
            return latency, energy
