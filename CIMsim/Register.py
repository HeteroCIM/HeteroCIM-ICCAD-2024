import configparser as cp
class RegFile():
    def __init__(self, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.read_latency = config.getfloat("RegFile", "read_latency")
        self.write_latency = config.getfloat("RegFile", "write_latency")
        self.size = config.getfloat("RegFile", "size")
        self.power = config.getfloat("RegFile", "power")
    def read(self, data_size, true_data=False):
        # data_size: bit
        if ~true_data:
            energy = self.read_latency * self.power
            return self.read_latency, energy
    def write(self, data_size, true_data=False):
        # data_size: bit
        if ~true_data:
            energy = self.write_latency * self.power
            return self.write_latency, energy