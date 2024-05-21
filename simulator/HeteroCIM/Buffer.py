import configparser as cp
from HeteroCIM.utils import merge_stats_add

class Buffer():
    # buffer and register file
    def __init__(self, name="default_buffer", config_path = "", key = "Buffer", parent = None):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.access_cycles = config.getfloat(key, "access_latency") if config.getfloat(key, "access_latency") != -1 else 1
        self.energy_per_bit = config.getfloat(key, "energy_per_bit") if config.getfloat(key, "energy_per_bit") != -1 else 1e-12
        self.size = config.getfloat(key, "size") if config.getfloat(key, "size") != -1 else 524288
        self.bit_width = config.getfloat(key, "bit_width") if config.getfloat(key, "bit_width") != -1 else 128*32
        self.buffer_frequency = config.getfloat(key, "buffer_frequency") if config.getfloat(key, "buffer_frequency") != -1 else 300e9
        self.name = name
        self.parent = parent
        self.busy = False
        self.area_dict = {
            32768: 21240.78, #4kB
            65536: 25091.68, #8kB
            131072: 29692.60, #16kB
            262144: 46839.87, #32kB
            524288: 85325.58, #64kB
            1048576: 185605.85, #128kB
            2097152: 304011.33, #256kB
            4194304: 3724077.22, #512kB
            8388608: 47964133.41, #1MB
            16777216: 6207121080.88, #2MB
        }
        if config.getfloat(key, "buffer_frequency") != -1:
            self.area = config.getfloat(key, "buffer_frequency")
        elif self.size in self.area_dict.keys():
            self.area = self.area_dict[self.size]
        else:
            assert(0), "no default area info for buffer size: " + str(self.size) + ". Please enter buffer area manually"
    def read(self, data_size, stats = {}):
        # data_size: bit
        latency = (self.access_cycles + data_size / self.bit_width) / self.buffer_frequency
        energy = data_size * self.energy_per_bit
        local_stats = {}
        local_stats[self.name + "_buf_r_T"] = latency
        local_stats[self.name + "_buf_r_E"] = energy
        merge_stats_add(stats, local_stats)
        return latency, energy
    def write(self, data_size, stats = {}):
        # data_size: bit
        latency = (self.access_cycles + data_size / self.bit_width) / self.buffer_frequency
        energy = data_size * self.energy_per_bit
        local_stats = {}
        local_stats[self.name + "_buf_w_T"] = latency
        local_stats[self.name + "_buf_w_E"] = energy
        merge_stats_add(stats, local_stats)
        return latency, energy
    def getArea(self):
        area = self.area_dict[self.size]
        return area