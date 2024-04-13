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
            # data of gen5 is accurate
            1: 6.5e-12,
            2: 6.5e-12,
            3: 6.5e-12,
            4: 6.5e-12,
            5: 6.5e-12,
            6: 6.5e-12,
        }
        self.bandwidth = self.single_direction_rate_dict[self.gen] * self.lanes
    def transmission(self, src, dst, data_size, stats = {}):
        T_src, E_src= src.read(data_size)
        T_dst, E_dst = dst.write(data_size)
        T_bus = data_size / self.bandwidth
        E_bus = data_size * self.energy_efficiency_dict[self.gen]
        # print("T_src: ", T_src, "T_dst", T_dst, "T_bus", T_bus)
        # print("src: ", src, "dst", dst)
        T = max(T_src, T_dst, T_bus)
        E = E_src + E_dst + E_bus
        return T, E