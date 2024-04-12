import configparser as cp
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.BLDrivers import *
from CIMsim.SLCollectors import *
from CIMsim.MAC import *
from CIMsim.Register import *
from CIMsim.MUX import *
from CIMsim.Buffer import *
from CIMsim.utils import *
from CIMsim.PE import *
from CIMsim.NonlinearVecModule import *
import numpy as np

class PCIe():
    def __init__(self, name, config_path):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.name = name
        self.gen = config.getint("PCIe", "gen")
        self.lanes = config.getint("PCIe", "lanes")
        self.PCIe_type = "PCIe" + str(self.gen) + "x" + str(self.lanes)
        self.single_direction_rate_dict = {
            # transmission rate per lane (single direction), unit: bit/s, 
            1: 2.5e9 * 8 / 10,
            2: 5e9 * 8 / 10,
            3: 8e9 * 128 / 130,
            4: 16e9 * 128 / 130,
            5: 32e9 * 128 / 130,
            6: 64e9 * 128 / 130,
        }
        self.energy_efficiency_dict = {
            # cannot get data
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }
        self.bandwidth = self.single_direction_rate_dict[self.gen] * self.lanes
    def transmission(self, src, dst, data_size, stats = {}):
        T_src, E_src= src.read()
        T_dst, E_dst = dst.write()
        T_bus = data_size / bandwidth
        T = max(T_src, T_dst, T_bus)
        E = E_src + E_dst
        return T, E