import configparser as cp
import math
import numpy as np
from CIMsim.utils import *
from CIMsim.MAC import *
from typing import List, Optional
# NVM means nonlinear vector module. NVM is responsible for nonlinear operations and SIMD vector operations

class LUT():
    # LUT for piecewise linear
    def __init__(self, n_samples, LUT_precision, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.n_samples = n_samples
        self.LUT_precision = LUT_precision
        self.mux_2_1_latency = 0.5e-9
        self.mux_2_1_power = 1.64e-6
        self.frequency = config.getfloat("NonlinearVecModule", "frequency")
        self.mac = MAC(config_path, self.frequency)
        ram_access_cycle = config.getfloat("LUT", "ram_access_cycle") if config.getfloat("LUT", "ram_access_cycle") != -1 else 1
        self.ram_access_latency = ram_access_cycle * 1 / self.frequency
        self.ram_energy_per_bit = config.getfloat("LUT", "ram_energy_per_bit") if config.getfloat("LUT", "ram_energy_per_bit") != -1 else 1e-12
        self.ram_area = config.getfloat("LUT", "ram_area") if config.getfloat("LUT", "ram_area") != -1 else 0.192
        comparisons = self.n_samples
        compare_T = self.mux_2_1_latency * comparisons / 2 # average
        compare_E = self.mux_2_1_power * comparisons / 2 * compare_T # average
        ram_T = self.ram_access_latency
        ram_E = self.ram_energy_per_bit * 3 * self.LUT_precision
        n_mux = 2 ** np.ceil(math.log(2,self.n_samples)) - 1
        mux_T = self.mux_2_1_latency * np.ceil(math.log(2,self.n_samples))
        mux_E = self.mux_2_1_power * n_mux * self.mux_2_1_latency
        self.LUT_T = compare_T + ram_T + mux_T
        self.LUT_E = compare_E + ram_E + mux_E
        self.LUT_size = 3 * self.n_samples * self.LUT_precision
        self.sram_area = self.LUT_size * self.ram_area

    def compute(self, input_shape: List[int]):
        cnt = 1
        for i in input_shape:
            cnt *= i
        total_T = self.LUT_T * cnt
        total_E = self.LUT_E * cnt
        return total_T, total_E
    def getArea(self):
        return self.sram_area

class NonlinearVecModule():
    def __init__(self, name = "", config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.name = name
        activation_func_list = ["ReLU", "GeLU", "Sigmond", "Tanh", "LeakyReLU", "ELU", "SiLU"]
        self.PWL_sample_dict = {
            "ReLU": {4:3, 8:3, 16:3, 32:3},
            "GeLU": {4:3, 8:11, 16:32, 32:407},
            "Sigmond": {4:3, 8:7, 16:28, 32:323},
            "Tanh": {4:3, 8:11, 16:40, 32:494},
            "LeakyReLU": {4:3, 8:3, 16:3, 32:3},
            "ELU": {4:3, 8:6, 16:24, 32:281},
            "SiLU": {4:3, 8:9, 16:36, 32:485}
        }
        self.activaton_module_dict = {}
        for func in activation_func_list:
            if config.getboolean("NonlinearVecModule", "has_" + func):
                use_LUT = config.getboolean(func, "use_LUT")
                if use_LUT:
                    LUT_dict = self.PWL_sample_dict[func]
                    self.PWL_precision = config.getint(func, "PWL_precision") # e.g. 8bit
                    self.LUT_precision = config.getint(func, "LUT_precision") # e.g. 8bit
                    self.n_samples = config.getint(func, "n_samples") if config.getint(func, "n_samples") != -1 else LUT_dict[self.PWL_precision]
                    lut = LUT(self.n_samples, self.LUT_precision, config_path)
                    self.activaton_module_dict[func] = lut
                else: 
                    assert(0), "TODO: regular computation"
    def compute(self, nvm_type: str, nvm_name: str, input_shape: List[int], stats = {}):
        if nvm_type == "activation":
            act_T, act_E = self.activaton_module_dict[nvm_name].compute(input_shape)
            local_stats = {}
            local_stats[self.name + "_" + nvm_name + "_T"] = act_T
            local_stats[self.name + "_" + nvm_name + "_E"] = act_E
            merge_stats_add(stats, local_stats)
            return act_T, act_E
        elif nvm_type == "vector":
            pass
        elif nvm_type == "reduce":
            pass



