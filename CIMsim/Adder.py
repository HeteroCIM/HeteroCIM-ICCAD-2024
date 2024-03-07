import configparser as cp
class Adder():
    # SIMD adder to sum up the computation results of input vector segments
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.latency = config.getfloat("Adder", "Adder_latency")
        self.energy = config.getfloat("Adder", "Adder_energy")
    def compute(self, input_len):
        return self.latency, self.energy