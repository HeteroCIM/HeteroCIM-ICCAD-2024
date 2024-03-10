import configparser as cp
class Buffer():
    def __init__(self, name="default_buffer", config_path = "", key = "Buffer"):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.access_latency = config.getfloat(key, "access_latency")
        self.energy_per_bit = config.getfloat(key, "energy_per_bit")
        self.size = config.getfloat(key, "size")
        self.bit_width = config.getfloat(key, "bit_width")
        self.buffer_frequency = config.getfloat(key, "buffer_frequency")
        self.name = name
    def read(self, data_size, true_data=False):
        # data_size: bit
        if ~true_data:
            latency = (self.access_latency + data_size / self.bit_width) / self.buffer_frequency
            energy = data_size * self.energy_per_bit
            return latency, energy
    def write(self, data_size, true_data=False):
        # data_size: bit
        if ~true_data:
            latency = (self.access_latency + data_size / self.bit_width) / self.buffer_frequency
            energy = data_size * self.energy_per_bit
            return latency, energy