import configparser as cp
class MAC():
    # this MAC is used to accumulate the single bit output into true outputs.
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.latency = config.getfloat("MAC", "MAC_latency")
        self.energy = config.getfloat("MAC", "MAC_energy")
    def compute(self):
        return self.latency, self.energy