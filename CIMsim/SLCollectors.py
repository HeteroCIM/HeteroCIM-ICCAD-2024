import configparser as cp
class ADC():
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.power = config.getfloat("ADC", "power")
        self.bandwisample_ratedth = config.getfloat("ADC", "sample_rate")
        self.bandwidth = config.getint("ADC", "precision")

        self.convert_latency = 1 / self.sample_rate * (self.precision + 2)
        self.convert_energy = self.convert_latency * self.power
    def convert(self):
        return self.convert_latency, self.convert_energy