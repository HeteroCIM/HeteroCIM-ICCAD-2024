import configparser as cp
class MAC():
    # this MAC is used to accumulate the single bit output into true outputs.
    def __init__(self, config_path = "", frequency = -1 ):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        if frequency == -1:
            frequency = config.getfloat("PE", "frequency")
        # default config comes from "Efficient Fixed/Floating-Point Merged Mixed-Precision Multiply-Accumulate Unit for Deep Learning Processors"
        cycles = config.getfloat("MAC", "MAC_latency") if config.getfloat("MAC", "MAC_latency")!= -1 else 2
        self.latency = cycles * 1 / frequency
        power = config.getfloat("MAC", "MAC_power") if config.getfloat("MAC", "MAC_power") != -1 else 6.65e-3
        self.energy = power * self.latency
        self.area = config.getfloat("MAC", "MAC_area") if config.getfloat("MAC", "MAC_area") != -1 else 1283.23
    def compute(self):
        return self.latency, self.energy
    def getArea(self):
        return self.area