import configparser as cp
class Buffer():
    def __init__(self, name, config_path = "", key = "Buffer"):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.read_latency = config.getfloat(key, "read_latency")
        self.write_latency = config.getfloat(key, "write_latency")
        self.power = config.getfloat(key, "power")
        self.size = config.getfloat(key, "size")
        self.name = name
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