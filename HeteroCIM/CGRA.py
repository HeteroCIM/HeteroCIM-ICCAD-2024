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
import numpy as np
class CGRA():
    def __init__(self, name, config_path = "") -> None:
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        type = config["CGRA"]["type"]
        if type == "OPU":
            self.name = name
            self.hardware = OPU()
        else:
            assert(0), "For now, we only support coarse-grained OPU model for CGRA config"
        self.CGRA_buf = Buffer(self.name + "_CGRA_buf", config_path, "CGRA Buffer", self)
        self.NVM_reg = Buffer(self.name + "_NVM_vreg", config_path, "NVM VREG", self)
        self.busy = False

    def compute_batmatmul(self, B, M, N, P, data_bits, stats = {}):
        T, E = self.hardware.compute_batmatmul(B, M, N, P, data_bits)
        local_stats = {}
        local_stats[self.name + "_CGRA_matmul_T"] = T
        local_stats[self.name + "_CGRA_matmul_E"] = E
        return T, E

    def compute_nvm(self, nvm_type: str, input_size, data_bits, stats = {}):
        T, E = self.hardware.compute_nvm(nvm_type, input_size, data_bits)
        local_stats = {}
        local_stats[self.name + "_CGRA_" + nvm_type + "_T"] = T
        local_stats[self.name + "_CGRA_" + nvm_type + "_E"] = E
        return T, E



class OPU():
    # paper cited
    def __init__(self) -> None:
        # NPE: An CGRA-based Overlay Processor for Natural Language Processing, 16bit
        self.frequency = 300e6
        self.softmax_throughput_dict = {
            16: 1.64,
            8: 3.05,
            4: 4.74,
            2: 6.40
        }
        self.layernorm_throughput_dict = {
            16: 0.64,
            8: 1.29,
            4: 2.42,
            2: 4.13
        }
        self.gelu_throughput_dict = {
            16: 4,
            8: 8,
            4: 16,
            2: 32
        }
        self.vector_throughput_dict = {}
        self.vector_throughput_dict["VectorAdd"] = {}
        self.vector_throughput_dict["VectorMul"] = {}
        self.vector_throughput_dict["VectorDiv"] = {
            # assume 64 dividers
            16: 3.2,
            8: 5.33,
            4: 8,
            2: 10.67
        }
        self.n_MAC = 512
        self.PE_power = 1.628 # watt
        self.NVM_power = 1.722 # watt
        
    def compute_batmatmul(self, B, M, N, P, data_bits):
        num_operations = B * M * N * P
        T = np.ceil(num_operations / self.n_MAC / 2) / self.frequency
        E = T * self.PE_power
        return T, E

    def compute_nvm(self, nvm_type: str, input_size, data_bits):
        throughput = 0
        if nvm_type == "ReduceSoftmax":
            throughput = self.softmax_throughput_dict[data_bits]
        elif nvm_type == "ReduceLayernorm":
            throughput = self.layernorm_throughput_dict[data_bits]
        elif nvm_type == "VectorGeLUPWL":
            throughput = self.gelu_throughput_dict[data_bits]
        else:
            if nvm_type not in self.vector_throughput_dict.keys():
                print(nvm_type)
                assert(0)
            else:
                throughput = self.vector_throughput_dict[nvm_type][data_bits]
        # TODO:check
        throughput = throughput * 2.5 #scaling of NPE paper
        T = np.ceil(input_size / throughput) / self.frequency
        E = T * self.PE_power
        return T, E


