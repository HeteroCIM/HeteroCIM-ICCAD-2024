import configparser as cp
class DAC():
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.power = config.getfloat("DAC", "power")
        self.sample_rate = config.getfloat("DAC", "sample_rate")
        self.precision = config.getint("DAC", "precision")
        if config.has_option("DAC", "latency"):
            self.convert_latency = config.getfloat("DAC", "latency")
        else:
            self.convert_latency = 1 / self.sample_rate * (self.precision + 2)
        self.convert_energy = self.convert_latency * self.power
    def convert(self):
        return self.convert_latency, self.convert_energy