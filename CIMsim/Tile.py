import configparser as cp
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.BLDrivers import *
from CIMsim.SLCollectors import *
from CIMsim.MAC import *
from CIMsim.Register import *
from CIMsim.MUX import *

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
        self.input_reg = RegFile(64 * 1024 * 8, config_path)
        self.output_reg = RegFile(64 * 1024 * 8, config_path) 
        self.inter_tile_bandwidth = config.getfloat("Tile", "inter_tile_bandwidth")
        self.name = name 
    def compute(self, vector_size = 64, active_col = 64):
        # the read latency&energy of global_buffer is calculated in the higher level, not this tile level
        # here "compute" means vector-matrix multiplication
        # write vector into reg file
        i_reg_W_T, i_reg_W_E = self.input_reg.write(vector_size * 8) # T: latency E: energy
        total_T = 0
        total_E = 0
        total_T += i_reg_W_T
        total_E += i_reg_W_E
        # driver pair: ADC/DAC
        if self.driver_pair == 1:
            # ######## if not latched, we need several rounds to input the vector and compute the whole MVM (TBD!)
            assert vector_size >= self.DAC_num
            cal_round = vector_size / self.DAC_num
            i_reg_r_T, i_reg_r_E = self.input_reg.read(self.DAC_num)
            dac_T, dac_E = self.dac.convert()
            dac_E *= self.DAC_num
            demux_T, demux_E = self.demux.execute()
            crossbar_T, crossbar_E = self.crossbar.compute(self.DAC_num)
            mux_T, mux_E = self.mux.execute()
            mux_E *= active_col
            mux_T *= (active_col / self.ADC_num)
            adc_T, adc_E = self.adc.convert()
            adc_E *= active_col # total number of conversion needed for one MVM
            adc_T *= (active_col / self.ADC_num) # number of cols that one ADC is responsible for
            mac_T, mac_E = self.mac.compute() # only calculate mac_T once, because the latency can be hide in the ADC latency
            mac_E *= active_col * (self.crossbar.bit_per_weight / self.crossbar.bit_per_cell)
            o_reg_W_T, o_reg_W_E = self.output_reg.write(active_col)
            total_T += (i_reg_r_T + dac_T + demux_T + crossbar_T + mux_T + adc_T + mac_T + o_reg_W_T) * cal_round
            total_E += (i_reg_r_E + dac_E + demux_E + crossbar_E + mux_E + adc_E + mac_E + o_reg_W_E) * cal_round
            # adder needed! not implemented yet really need? or pipelined?
        #o_reg_W_T, o_reg_W_E = self.output_reg.write(vector_size * 8)
        return total_T, total_E
    def update(self):
        assert 0 , "write to mem not implemented"
    