import configparser as cp
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.BLDrivers import *
from CIMsim.SLCollectors import *
from CIMsim.MAC import *

# a crossbar array tile
class Tile():
    def __init__(self, tile_config_path = ""):
        config = cp.ConfigParser()
        config.read(tile_config_path)
        assert tile_config_path != "", "cannot find config file!"
        # self.power = config.getfloat("ADC", "power")
        # self.bandwisample_ratedth = config.getfloat("ADC", "sample_rate")
        # self.bandwidth = config.getint("ADC", "precision")
        self.tile_config_path = tile_config_path
        self.driver_pair = config.getint("Tile", "driver_pair")
        if self.driver_pair == 1:
            self.DAC_num = config.getint("Tile", "DAC_num")
            self.ADC_num = config.getint("Tile", "ADC_num")
            self.adc = ADC(tile_config_path)
            self.dac = DAC(tile_config_path)
        else:
            assert False, "not implemented yet"
        self.crossbar = Crossbar(tile_config_path)
        self.mac = MAC(tile_config_path)
    def compute(self):

        pass
    