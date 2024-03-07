import configparser as cp
class MUX():
    # this MAC is used to accumulate the single bit output into true outputs.
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.latency = config.getfloat("MUX", "MUX_latency")
        self.energy = config.getfloat("MUX", "MUX_energy")
    def execute(self):
        return self.latency, self.energy

class DeMUX():
    # this MAC is used to accumulate the single bit output into true outputs.
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.latency = config.getfloat("DeMUX", "DeMUX_latency")
        self.energy = config.getfloat("DeMUX", "DeMUX_energy")
    def execute(self):
        return self.latency, self.energy