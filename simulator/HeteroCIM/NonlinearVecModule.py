import configparser as cp
import math
import numpy as np
from HeteroCIM.utils import *
from HeteroCIM.MAC import *
from HeteroCIM.Buffer import *
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
        self.mac_T, self.mac_E = self.mac.compute()
        n_mux = 2 ** np.ceil(math.log(2,self.n_samples)) - 1
        mux_T = self.mux_2_1_latency * np.ceil(math.log(2,self.n_samples))
        mux_E = self.mux_2_1_power * n_mux * self.mux_2_1_latency
        self.LUT_T = compare_T + ram_T + mux_T
        self.LUT_E = compare_E + ram_E + mux_E
        self.LUT_size = 3 * self.n_samples * self.LUT_precision
        self.sram_area = self.LUT_size * self.ram_area
        self.parallelism = config.getint("NonlinearVecModule", "parallelism") if config.getfloat("NonlinearVecModule", "parallelism") != -1 else 64
        self.busy = False

    def compute(self, input_shape: List[int]):
        cnt = 1
        for i in input_shape:
            cnt *= i
        # print("debug: LUT: ", self.LUT_T)
        # print("debug: LUT: ", self.mac_T)
        total_T = (self.LUT_T + self.mac_T) * cnt / self.parallelism
        total_E = (self.LUT_E + self.mac_E) * cnt
        return total_T, total_E
    def getArea(self):
        return self.sram_area * self.parallelism

class NonlinearVecModule():
    def __init__(self, name = "", config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.name = name
        self.frequency = config.getfloat("NonlinearVecModule", "frequency")
        self.busy = False
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
        self.nvm_buf = Buffer(self.name + "_input_buf", config_path, "NonlinearVectorModule Buffer", self)
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
        self.vector_throughput_dict = {}
        self.vector_throughput_dict["VectorAdd"] = {
            # assume 64 adders
            16: 64,
            8: 128,
            4: 256,
            2: 512
        }
        self.vector_throughput_dict["VectorDiv"] = {
            # assume 64 dividers
            16: 3.2,
            8: 5.33,
            4: 8,
            2: 10.67
        }
        self.reduce_throughput_dict = {}
        self.reduce_throughput_dict["ReduceSoftmax"] = {
            16: 1.64,
            8: 3.05,
            4: 4.74,
            2: 6.40
        }
        self.reduce_throughput_dict["ReduceLayernorm"] = {
            16: 0.64,
            8: 1.29,
            4: 2.42,
            2: 4.13
        }
    def compute(self, nvm_type: str, nvm_name: str, input_shape: List[int], data_bits, stats = {}):
        total_T = 0
        total_E = 0
        local_stats = {}
        n_elements = 1
        for i in input_shape:
            n_elements *= i
        nvm_buf_T, nvm_buf_E = self.nvm_buf.read(n_elements * 8)
        total_T += nvm_buf_T
        total_E += nvm_buf_E
        local_stats[self.name + "_buf_T"] = nvm_buf_T
        local_stats[self.name + "_buf_E"] = nvm_buf_E

        if nvm_type == "Vector" and (nvm_name[6:] in self.activaton_module_dict.keys()):
            nvm_name = nvm_name[6:]
            # activation function
            act_T, act_E = self.activaton_module_dict[nvm_name].compute(input_shape)
            total_T += act_T
            total_E += act_E
            local_stats[self.name + "_" + nvm_name + "_LUT_T"] = act_T
            local_stats[self.name + "_" + nvm_name + "_LUT_E"] = act_E
            merge_stats_add(stats, local_stats)
            return total_T, total_E
        elif nvm_type == "Vector" and (nvm_name in self.vector_throughput_dict):
            throughput = self.vector_throughput_dict[nvm_name][data_bits]
            T = np.ceil(n_elements / throughput) / self.frequency
            E = T * 0.1 # TODO: check
            local_stats[self.name + "_" + nvm_name + "_T"] = T
            local_stats[self.name + "_" + nvm_name + "_E"] = E
            merge_stats_add(stats, local_stats)
            return T, E
        elif nvm_type == "Reduce":
            throughput = self.reduce_throughput_dict[nvm_name][data_bits]
            T = np.ceil(n_elements / throughput) / self.frequency
            E = T * 1.722 # TODO: check
            local_stats[self.name + "_" + nvm_name + "_T"] = T
            local_stats[self.name + "_" + nvm_name + "_E"] = E
            merge_stats_add(stats, local_stats)
            return T, E
        else:
            print(nvm_type, nvm_name)
            assert(0)
    def getArea(self, stats):
        local_stats = {}
        total_area = 0
        for name in self.activaton_module_dict.keys():
            hardware = self.activaton_module_dict[name]
            total_area += hardware.getArea()
            local_stats["NVM_" + name + "_area"] = hardware.getArea()
        merge_stats_add(stats, local_stats)
        return total_area



