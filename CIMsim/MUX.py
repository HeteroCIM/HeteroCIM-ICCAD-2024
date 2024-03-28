import configparser as cp
import numpy as np
import math
class MUX():
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.mux_2_1_latency = 0.5e-9
        self.mux_2_1_power = 1.64e-6
        self.ways = config.getfloat("MUX", "MUX_ways") if config.getfloat("MUX", "MUX_ways") != -1 else 2
        if config.getfloat("MUX", "MUX_latency") != -1:
            self.latency = config.getfloat("MUX", "MUX_latency") 
        else:
            self.latency = self.mux_2_1_latency * np.ceil(math.log(2, self.ways))
        if config.getfloat("MUX", "MUX_energy") != -1:
            self.energy = config.getfloat("MUX", "MUX_energy")
        else:
            self.energy = self.mux_2_1_power * (2 ** np.ceil(math.log(2, self.ways)) - 1) * self.latency
        # MUX area is small enough to be ignored
        self.area = config.getfloat("MUX", "MUX_rea") if config.getfloat("MUX", "MUX_rea") != -1 else 0
    def execute(self):
        return self.latency, self.energy
    def getArea(self):
        return self.area

class DeMUX():
    def __init__(self, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.demux_2_1_latency = 0.5e-9
        self.demux_2_1_power = 1.64e-6
        self.ways = config.getfloat("DeMUX", "DeMUX_ways") if config.getfloat("DeMUX", "DeMUX_ways") != -1 else 2
        if config.getfloat("DeMUX", "DeMUX_latency") != -1:
            self.latency = config.getfloat("DeMUX", "DeMUX_latency") 
        else:
            self.latency = self.demux_2_1_latency * np.ceil(math.log(2, self.ways))

        if config.getfloat("DeMUX", "DeMUX_energy") != -1:
            self.energy = config.getfloat("DeMUX", "DeMUX_energy")
        else:
            self.energy = self.demux_2_1_power * (2 ** np.ceil(math.log(2, self.ways)) - 1) * self.latency
        # DeMUX area is small enough to be ignored
        self.area = config.getfloat("MUX", "MUX_rea") if config.getfloat("MUX", "MUX_rea") != -1 else 0
            
    def execute(self):
        return self.latency, self.energy
    def getArea(self):
        return self.area