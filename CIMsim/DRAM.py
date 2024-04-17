import configparser as cp
import os
import json
from CIMsim.utils import *
class DRAM():
    def __init__(self, name, config_path = ""):
        assert config_path != "", "cannot find config file!"
        self.name = name
        config = cp.ConfigParser()
        config.read(config_path)
        self.model_type = config["DRAM model"]["backend_model"]
        if self.model_type == "CIMsim":
            self.size = config.getfloat("CIMsim model", "size")
            self.energy_per_bit = config.getfloat("CIMsim model", "energy_per_bit")
            self.bit_width = config.getint("CIMsim model", "bit_width") if config.getint("CIMsim model", "bit_width") != -1 else 512
            self.read_access_latency = config.getfloat("CIMsim model", "read_access_latency")
            self.write_access_latency = config.getfloat("CIMsim model", "write_access_latency")
            self.DRAM_frequency = config.getfloat("CIMsim model", "DRAM_frequency")
        elif self.model_type == "DRAMsim3":
            self.DRAM_type = config["DRAMsim3 model"]["DRAM_type"]
            self.DRAM_size = config["DRAMsim3 model"]["DRAM_size"]
            self.device_width = config["DRAMsim3 model"]["device_width"]
            self.DRAM_frequency = config.getint("DRAMsim3 model", "DRAM_frequency")
            self.bus_width = config.getint("DRAMsim3 model", "bus_width")
            self.DRAMsim3_dir = "DRAMsim3/"
            self.DRAMsim3_exe_path = self.DRAMsim3_dir + "build/dramsim3main"
            self.DRAMsim3_trace_gen_path = self.DRAMsim3_dir + "CIMsim_scripts/trace_gen_CIMsim.py"
            self.DRAMsim3_trace_dir_path = self.DRAMsim3_dir + "CIMsim_traces/"
            self.DRAMsim3_res_dir_path = self.DRAMsim3_dir + "CIMsim_results/"
            self.DRAMsim3_config_filename = self.DRAMsim3_dir + "configs/" + self.DRAM_type + "_" + self.DRAM_size + "_x" + self.device_width + "_" + str(self.DRAM_frequency) + ".ini"
            self.trace_count = 0
        else:
            assert(0), "cannot find dram model backend. Now support CIMsim and DRAMsim3 only"
        self.busy = False

    def read(self, data_size, stats = {}, ):
        # data_size: bit
        if self.model_type == "CIMsim":
            latency = (self.read_access_latency + data_size / self.bit_width) / self.DRAM_frequency
            energy = self.energy_per_bit * data_size
        elif self.model_type == "DRAMsim3":
            n_requests = int(data_size / self.bus_width)
            # generate trace
            name = "DRAM_read_" + str(self.trace_count)
            self.trace_count += 1
            os.system("python " + self.DRAMsim3_trace_gen_path + " -n " + str(n_requests) + " -b " +  str(self.bus_width) + " -r 100000000 -s stream -f dramsim3 -o " +  self.DRAMsim3_trace_dir_path + " -m " + name)
            # run DRAMsim3
            # print("./" + self.DRAMsim3_exe_path + " " + self.DRAMsim3_config_filename + " -c 100000 -t " +  self.DRAMsim3_trace_dir_path + name)
            os.system("./" + self.DRAMsim3_exe_path + " " + self.DRAMsim3_config_filename + " -c 100000 -t " +  self.DRAMsim3_trace_dir_path + name + " -o " + self.DRAMsim3_res_dir_path)
            # read results
            with open(self.DRAMsim3_res_dir_path + "dramsim3.json",'r', encoding='utf8') as js:
                json_data = json.load(js)
            avg_cycles = json_data["0"]["average_read_latency"]
            latency = avg_cycles * n_requests * (1 / self.DRAM_frequency / 1e6)
            energy = json_data["0"]["read_energy"] * 1e-12
        else:
            assert(0), "cannot find dram model backend. Now support CIMsim and DRAMsim3 only"
        # stats
        local_stats = {}
        local_stats[self.name + "_dram_r_T"] = latency
        local_stats[self.name + "_dram_r_E"] = energy
        merge_stats_add(stats, local_stats)
        return latency, energy
    def write(self, data_size, stats = {}):
        # data_size: bit
        if self.model_type == "CIMsim":
            latency = (self.write_access_latency + data_size / self.bit_width) / self.DRAM_frequency
            energy = self.energy_per_bit * data_size
        elif self.model_type == "DRAMsim3":
            n_requests = int(data_size / self.bus_width)
            # generate trace
            name = "DRAM_read_" + str(self.trace_count)
            self.trace_count += 1
            os.system("python " + self.DRAMsim3_trace_gen_path + " -n " + str(n_requests) + " -b " +  str(self.bus_width) + " -r 0 -s stream -f dramsim3 -o " +  self.DRAMsim3_trace_dir_path + " -m " + name)
            # run DRAMsim3
            # print("./" + self.DRAMsim3_exe_path + " " + self.DRAMsim3_config_filename + " -c 100000 -t " +  self.DRAMsim3_trace_dir_path + name)
            os.system("./" + self.DRAMsim3_exe_path + " " + self.DRAMsim3_config_filename + " -c 100000 -t " +  self.DRAMsim3_trace_dir_path + name + " -o " + self.DRAMsim3_res_dir_path)
            # read results
            with open(self.DRAMsim3_res_dir_path + "dramsim3.json",'r', encoding='utf8') as js:
                json_data = json.load(js)
            write_cycles_dict = json_data["0"]["write_latency"]
            write_cycles = 0
            for key in write_cycles_dict.keys():
                write_cycles += int(key) * int(write_cycles_dict[key])
            latency = write_cycles * (1 / self.DRAM_frequency / 1e6)
            energy = json_data["0"]["write_energy"] * 1e-12
        else:
            assert(0), "cannot find dram model backend. Now support CIMsim and DRAMsim3 only"
        # stats
        local_stats = {}
        local_stats[self.name + "_dram_w_T"] = latency
        local_stats[self.name + "_dram_w_E"] = energy
        merge_stats_add(stats, local_stats)
        return latency, energy
