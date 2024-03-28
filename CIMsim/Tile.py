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

# a crossbar array tile
class Tile():
    def __init__(self, name, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        # self.power = config.getfloat("ADC", "power")
        # self.bandwisample_ratedth = config.getfloat("ADC", "sample_rate")
        # self.bandwidth = config.getint("ADC", "precision")
        self.config_path = config_path
        self.driver_pair = config.getint("Tile", "driver_pair")
        if self.driver_pair == 1:
            self.DAC_num = config.getint("Tile", "DAC_num")
            self.ADC_num = config.getint("Tile", "ADC_num")
            self.adc = ADC(config_path)
            self.dac = DAC(config_path)
            self.mux = MUX(config_path)
            self.demux = DeMUX(config_path)
        else:
            assert False, "not implemented yet"
        self.crossbar = Crossbar(config_path)
        self.mac = MAC(config_path)
        self.name = name 
        self.input_buf = Buffer(self.name + "_input_buf", config_path, "Input Buffer")
        self.output_buf = Buffer(self.name + "_output_buf", config_path, "Output Buffer") 
        self.inter_tile_bandwidth = config.getfloat("Tile", "inter_tile_bandwidth")
        self.frequency = config.getfloat("Tile", "frequency")

        
    def compute(self, vector_size = 64, active_col = 64, stats = {}):
        # the read latency&energy of global_buffer is calculated in the higher level, not this tile level
        # here "compute" means vector-matrix multiplication
        # write vector into reg file
        i_reg_W_T, i_reg_W_E = self.input_buf.write(vector_size * 8) # T: latency E: energy
        total_T = 0
        total_E = 0
        total_T += i_reg_W_T
        total_E += i_reg_W_E
        # driver pair: ADC/DAC
        if self.driver_pair == 1:
            # ######## if not latched, we need several rounds to input the vector and compute the whole MVM (TBD!)
            assert vector_size >= self.DAC_num
            cal_round = vector_size / self.DAC_num
            i_buf_r_T, i_buf_r_E = self.input_buf.read(self.DAC_num)
            dac_T, dac_E = self.dac.convert()
            dac_E *= self.DAC_num
            demux_T, demux_E = self.demux.execute()
            crossbar_T, crossbar_E = self.crossbar.compute(self.DAC_num, active_col)
            mux_T, mux_E = self.mux.execute()
            mux_E *= active_col
            mux_T *= (active_col / self.ADC_num)
            adc_T, adc_E = self.adc.convert()
            adc_E *= active_col # total number of conversion needed for one MVM
            adc_T *= (active_col / self.ADC_num) # number of cols that one ADC is responsible for
            mac_T, mac_E = self.mac.compute() # only calculate mac_T once, because the latency can be hide in the ADC latency
            #print("debug: mac_E:",mac_E,"times:",active_col * (self.crossbar.weight_bits / self.crossbar.mem_bits),"debug: mac_T:",mac_T)
            mac_E *= active_col * (self.crossbar.weight_bits / self.crossbar.mem_bits)
            o_buf_W_T, o_buf_W_E = self.output_buf.write(active_col)
            total_T += (i_buf_r_T + dac_T + demux_T + crossbar_T + mux_T + adc_T + mac_T + o_buf_W_T) * cal_round
            total_E += (i_buf_r_E + dac_E + demux_E + crossbar_E + mux_E + adc_E + mac_E + o_buf_W_E) * cal_round
            # adder needed! not implemented yet really need? or pipelined?
            local_stats = {}
            local_stats[self.name + "_i_buf_r_T"] = i_buf_r_T
            local_stats[self.name + "_i_buf_r_E"] = i_buf_r_E
            local_stats[self.name + "_dac_T"] = dac_T
            local_stats[self.name + "_dac_E"] = dac_E
            local_stats[self.name + "_demux_T"] = demux_T
            local_stats[self.name + "_demux_E"] = demux_E
            local_stats[self.name + "_crossbar_T"] = crossbar_T
            local_stats[self.name + "_crossbar_E"] = crossbar_E
            local_stats[self.name + "_mux_T"] = mux_T
            local_stats[self.name + "_mux_E"] = mux_E
            local_stats[self.name + "_adc_T"] = adc_T
            local_stats[self.name + "_adc_E"] = adc_E
            local_stats[self.name + "_mac_T"] = mac_T
            local_stats[self.name + "_mac_E"] = mac_E
            local_stats[self.name + "_o_buf_W_T"] = o_buf_W_T
            local_stats[self.name + "_o_buf_W_E"] = o_buf_W_E
            merge_stats_add(stats, local_stats)
            return total_T, total_E
        #o_buf_W_T, o_buf_W_E = self.output_buf.write(vector_size * 8)
    def update(self):
        assert 0 , "write to mem not implemented"
    
    def getArea(self, stats = {}):
        if self.driver_pair == 1:
            assert(0), "buf area needed!"
            mux_area = self.mux.getArea()
            demux_area = self.demux.getArea()
            dac_area = self.dac.getArea()
            adc_area = self.adc.getArea()
            crossbar_area = self.crossbar.getArea()
            #total_E += (i_buf_r_E + dac_E + demux_E + crossbar_E + mux_E + adc_E + mac_E + o_buf_W_E) * cal_round