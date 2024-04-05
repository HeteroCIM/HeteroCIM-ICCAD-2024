import configparser as cp
class DAC():
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.precision = config.getint("DAC", "precision")
        self.sample_rate = config.getfloat("DAC", "sample_rate") if config.getfloat("DAC", "sample_rate") != -1 else 1e9
        if config.getfloat("DAC", "latency") != -1:
            self.convert_latency = config.getfloat("DAC", "latency")
        else:
            self.convert_latency = 1 / self.sample_rate * (self.precision + 2)

        # default config comes from "ISAAC: A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars"
        self.power = config.getfloat("DAC", "power") if config.getfloat("DAC", "power") != -1 else 0.004 * 2 ** self.precision
        self.area = config.getfloat("DAC", "area") if config.getfloat("DAC", "area") != -1 else 170 * 2 ** self.precision
        self.convert_energy = self.convert_latency * self.power
    def convert(self):
        return self.convert_latency, self.convert_energy
    def getArea(self):
        return self.area

class PWM():
    def __init__(self, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.precision = config.getint("PWM", "precision")
        self.tick = config.getfloat("PWM", "tick")
        self.area = config.getfloat("PWM", "area")
        self.power = config.getfloat("PWM", "power")

    def convert(self, precision = -1):
        if precision == -1:
            precision = self.precision
        self.latency = 2 ** precision * self.tick
        self.energy = self.power * self.latency
        return self.latency, self.energy
    def getArea(self):
        return self.area
