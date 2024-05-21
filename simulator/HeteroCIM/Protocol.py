import configparser as cp
from HeteroCIM.DRAM import *
from HeteroCIM.Crossbar import *
from HeteroCIM.BLDrivers import *
from HeteroCIM.SLCollectors import *
from HeteroCIM.MAC import *
from HeteroCIM.MUX import *
from HeteroCIM.Buffer import *
from HeteroCIM.utils import *
from HeteroCIM.PE import *
from HeteroCIM.NonlinearVecModule import *
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
        self.util = config.getfloat("PCIe", "utilization") if config.getfloat("PCIe", "utilization") != -1 else 0.7
        self.busy = False
    def transmission(self, src, dst, data_size, stats = {}):
        T_src, E_src= src.read(data_size)
        T_dst, E_dst = dst.write(data_size)
        T_bus = data_size / self.bandwidth / self.util
        E_bus = data_size * self.energy_efficiency_dict[self.gen]
        T = max(T_src, T_dst, T_bus)
        E = E_src + E_dst + E_bus
        return T, E


class UCIe():
    def __init__(self, name, config_path):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.name = name
        self.lanes = config.getint("UCIe", "lanes")
        self.package_type = config["UCIe"]["package_type"]
        self.PCIe_type = "UCIe1.0 x" + str(self.lanes)
        self.rate_per_lane = 32e9 * 128 / 130 # PCIe gen5
        self.energy_efficiency_dict = {
            "standard": 0.5e-12,
            "advanced": 0.25e-12
        }
        self.bandwidth = self.rate_per_lane * self.lanes
        self.util = config.getfloat("UCIe", "utilization") if config.getfloat("UCIe", "utilization") != -1 else 0.7
        self.latency = 2e-9
        self.busy = False
    def transmission(self, src, dst, data_size, stats = {}):
        T_src, E_src= src.read(data_size)
        T_dst, E_dst = dst.write(data_size)
        T_bus = self.latency + data_size / self.bandwidth / self.util
        E_bus = data_size * self.energy_efficiency_dict[self.package_type]
        T = max(T_src, T_dst, T_bus)
        E = E_src + E_dst + E_bus
        return T, E

class CXL():
    # CXL3.0
    def __init__(self, name, config_path):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.name = name
        self.transmission_rate = 64e9 * 128 / 130 # PCIe gen5
        self.energy_efficiency = 6.5e-12
        self.bandwidth = self.transmission_rate
        self.util = config.getfloat("CXL", "utilization") if config.getfloat("CXL", "utilization") != -1 else 0.7
        self.busy = False
    def transmission(self, src, dst, data_size, stats = {}):
        T_src, E_src= src.read(data_size)
        T_dst, E_dst = dst.write(data_size)
        T_bus = data_size / self.bandwidth / self.util
        E_bus = data_size * self.energy_efficiency
        T = max(T_src, T_dst, T_bus)
        E = E_src + E_dst + E_bus
        return T, E