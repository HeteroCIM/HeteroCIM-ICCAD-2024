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
import numpy as np

# a crossbar array PE
class PE(): 
    def __init__(self, name, config_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.name = name
        self.config_path = config_path
        self.driver_pair = config.getint("PE", "driver_pair")
        if self.driver_pair == 1:
            self.DAC_num = config.getint("PE", "DAC_num")
            self.ADC_num = config.getint("PE", "ADC_num")
            self.adc = ADC(config_path)
            self.dac = DAC(config_path)
            self.mux = MUX(config_path)
            self.demux = DeMUX(config_path)
            self.input_buf = Buffer(self.name + "_input_buf", config_path, "Input Buffer")
            self.output_buf = Buffer(self.name + "_output_buf", config_path, "Output Buffer") 
            self.inter_PE_bandwidth = config.getfloat("PE", "inter_PE_bandwidth")
            self.mac = MAC(config_path)
            self.frequency = config.getfloat("PE", "frequency")
        elif self.driver_pair == 2:
            self.PWM = PWM(config_path)
            self.PWM_num = config.getint("PE", "PWM_num")
            self.ADC_num = config.getint("PE", "ADC_num")
            self.pulse_precision = config['PE']['pulse_precision'].split(',')
            for i in range(len(self.pulse_precision)):
                self.pulse_precision[i] = int(self.pulse_precision[i])
            self.adc = ADC(config_path)
            self.mux = MUX(config_path)
            self.input_buf = Buffer(self.name + "_input_buf", config_path, "Input Buffer")
            self.output_buf = Buffer(self.name + "_output_buf", config_path, "Output Buffer") 
            self.mac = MAC(config_path)

        elif self.driver_pair == 3:
            self.gen_PWM = config.getboolean("PE", "gen_PWM")
            if self.gen_PWM:
                self.PWM = PWM(config_path)
                self.PWM_num = config.getint("PE", "PWM_num")
            self.cap_ramp = CapRamp(config_path)
            self.cap_num = config.getint("PE", "cap_num")
        else:
            assert False, "not implemented yet"
        self.crossbar = Crossbar(config_path)
        self.weight_bits = config.getint("crossbar", "weight_bits")
        self.mem_bits = config.getint("crossbar", "mem_bits")
        self.name = name
        

        
    def compute(self, vector_size, active_rows = -1, active_cols = -1, stats = {}):
        total_T = 0
        total_E = 0
        if active_cols != -1:
            active_cols = active_cols * self.weight_bits / self.mem_bits * 2
        # driver pair: 1: ADC/DAC
        if self.driver_pair == 1:
            if active_rows == -1:
                # print(self.DAC_num, vector_size)
                active_rows = min(self.DAC_num, vector_size)
            if active_cols == -1:
                active_cols = self.crossbar.n_cols
            self.cols_per_adc = self.crossbar.n_cols / self.ADC_num
            cal_round = np.ceil(vector_size / active_rows) * np.ceil(self.cols_per_adc) # modified 4-3
            i_buf_r_T, i_buf_r_E = self.input_buf.read(active_rows)
            dac_T, dac_E = self.dac.convert()
            dac_E = dac_E * active_rows
            demux_T, demux_E = self.demux.execute()
            crossbar_T, crossbar_E = self.crossbar.compute(active_rows, active_cols)
            mux_T, mux_E = self.mux.execute()
            mux_E *= active_cols
            mux_T *= (active_cols / self.ADC_num)
            adc_T, adc_E = self.adc.convert()
            adc_E *= active_cols # total number of conversion needed for one MVM
            adc_T *= (active_cols / self.ADC_num) # number of cols that one ADC is responsible for
            # print(adc_T, adc_E, active_cols)
            # assert(0)
            mac_T, mac_E = self.mac.compute() # only calculate mac_T once, because the latency can be hide in the ADC latency
            #print("debug: mac_E:",mac_E,"times:",active_cols * (self.crossbar.weight_bits / self.crossbar.mem_bits),"debug: mac_T:",mac_T)
            mac_E *= active_cols * (self.crossbar.weight_bits / self.crossbar.mem_bits)
            o_buf_W_T, o_buf_W_E = self.output_buf.write(active_cols)
            total_T = total_T + (i_buf_r_T + dac_T + demux_T + crossbar_T + mux_T + adc_T + mac_T + o_buf_W_T) * cal_round
            total_E = total_E + (i_buf_r_E + dac_E + demux_E + crossbar_E + mux_E + adc_E + mac_E + o_buf_W_E) * cal_round
            # adder needed! not implemented yet really need? or gen_PWM?
            local_stats = {}
            local_stats[self.name + "_i_buf_r_T"] = i_buf_r_T * cal_round
            local_stats[self.name + "_dac_T"] = dac_T * cal_round
            local_stats[self.name + "_demux_T"] = demux_T * cal_round
            local_stats[self.name + "_crossbar_T"] = crossbar_T * cal_round
            local_stats[self.name + "_mux_T"] = mux_T * cal_round
            local_stats[self.name + "_adc_T"] = adc_T * cal_round
            local_stats[self.name + "_mac_T"] = mac_T * cal_round
            local_stats[self.name + "_o_buf_W_T"] = o_buf_W_T * cal_round

            local_stats[self.name + "_i_buf_r_E"] = i_buf_r_E * cal_round
            local_stats[self.name + "_dac_E"] = dac_E * cal_round
            local_stats[self.name + "_demux_E"] = demux_E * cal_round
            local_stats[self.name + "_crossbar_E"] = crossbar_E * cal_round
            local_stats[self.name + "_mux_E"] = mux_E * cal_round
            local_stats[self.name + "_adc_E"] = adc_E * cal_round
            local_stats[self.name + "_mac_E"] = mac_E * cal_round
            local_stats[self.name + "_o_buf_W_E"] = o_buf_W_E * cal_round

            merge_stats_add(stats, local_stats)
            return total_T, total_E

        elif self.driver_pair == 2:
            if active_rows == -1:
                active_rows = min(vector_size, self.PWM_num)
            if active_cols == -1:
                active_cols = self.crossbar.n_cols
            self.cols_per_adc = self.crossbar.n_cols / self.ADC_num
            cal_round = np.ceil(vector_size / active_rows) * np.ceil(self.cols_per_adc)
            print("cal_round", cal_round)
            local_stats = {}
            total_T, total_E = 0, 0
            PWM_T, PWM_E, crossbar_T, crossbar_E, ADC_T, ADC_E, mux_T, mux_E, i_buf_r_T, i_buf_r_E, o_buf_W_T, o_buf_W_E, mac_T, mac_E = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            max_p_bit = max(self.pulse_precision)
            for p_bits in self.pulse_precision:
                # i_buf
                i_buf_r_t, i_buf_r_e = self.input_buf.read(active_rows)
                i_buf_r_T = i_buf_r_t * cal_round
                i_buf_r_E = i_buf_r_e * cal_round
                # PWM
                PWM_t, PWM_e = self.PWM.convert(precision = max_p_bit)
                PWM_T += PWM_t * cal_round
                PWM_E += PWM_e * self.PWM_num * cal_round
                # crossbar
                crossbar_t, crossbar_e = self.crossbar.compute(active_rows, active_cols)
                crossbar_T += crossbar_t * cal_round
                crossbar_E += crossbar_e * cal_round
                # ADC
                adc_t, adc_e = self.adc.convert()
                adc_e *= active_cols # total number of conversion needed for one MVM
                adc_t *= (active_cols / self.ADC_num) # number of cols that one ADC is responsible for
                ADC_T += adc_t * cal_round
                ADC_E += adc_e * cal_round
                # MUX
                mux_t, mux_e = self.mux.execute()
                mux_e *= active_cols
                mux_t *= (active_cols / self.ADC_num)
                mux_T += mux_t * cal_round
                mux_E += mux_e * cal_round
                # mac (digital accumulate)
                mac_t, mac_e = self.mac.compute()
                mac_e *= active_cols * (self.crossbar.weight_bits / self.crossbar.mem_bits)
                mac_T += mac_t * cal_round
                mac_E += mac_e * cal_round
            # o_buf
            o_buf_W_t, o_buf_W_e = self.output_buf.write(active_cols)
            o_buf_W_T += o_buf_W_t
            o_buf_W_E += o_buf_W_e
            total_T = total_T + PWM_T + crossbar_T + ADC_T + mux_T + i_buf_r_T + o_buf_W_T + mac_T
            total_E = total_E + PWM_E + crossbar_E + ADC_E + mux_E + i_buf_r_E + o_buf_W_E + mac_E
            local_stats[self.name + "_PWM_T"] = PWM_T
            local_stats[self.name + "_crossbar_T"] = crossbar_T
            local_stats[self.name + "_ADC_T"] = ADC_T
            local_stats[self.name + "_mux_T"] = mux_T
            local_stats[self.name + "_i_buf_r_T"] = i_buf_r_T
            local_stats[self.name + "_o_buf_W_T"] = o_buf_W_T
            local_stats[self.name + "_mac_T"] = mac_T
            local_stats[self.name + "_PWM_E"] = PWM_E
            local_stats[self.name + "_crossbar_E"] = crossbar_E
            local_stats[self.name + "_ADC_E"] = ADC_E
            local_stats[self.name + "_mux_E"] = mux_E
            local_stats[self.name + "_i_buf_r_E"] = i_buf_r_E
            local_stats[self.name + "_o_buf_W_E"] = o_buf_W_E
            local_stats[self.name + "_mac_E"] = mac_E
            merge_stats_add(stats, local_stats)
            return total_T, total_E

        elif self.driver_pair == 3:
            if active_rows == -1:
                active_rows = np.min((self.PWM_num, vector_size)) if self.gen_PWM else vector_size
            if active_cols == -1:
                active_cols = self.crossbar.n_cols
            local_stats = {}
            total_T, total_E = 0, 0
            self.cols_per_cap = self.crossbar.n_cols / self.cap_num
            # each time, the capacitor can only collect the charge of one pos weight and one neg weight
            cal_round = np.ceil(vector_size / active_rows) * np.ceil(self.cols_per_cap / 2)
            # print("cal_round:", cal_round, "vector_size:", vector_size, "active_rows:", active_rows, "active_cols:", active_cols, "self.cap_num:", self.cap_num)
            # print("cal_round:", cal_round)
            if self.gen_PWM:
                PWM_T, PWM_E = self.PWM.convert()
                PWM_E = PWM_E * self.PWM_num * cal_round
                PWM_T *= cal_round
                total_T += PWM_T
                total_E += PWM_E
                local_stats[self.name + "_PWM_T"] = PWM_T
                local_stats[self.name + "_PWM_E"] = PWM_E
            cap_ramp_T, cap_ramp_E = self.cap_ramp.convert()
            cap_ramp_T *= cal_round
            cap_ramp_E *= active_cols * cal_round
            total_T += cap_ramp_T
            total_E += cap_ramp_E
            local_stats[self.name + "_cap_ramp_T"] = cap_ramp_T
            local_stats[self.name + "_cap_ramp_E"] = cap_ramp_E
            merge_stats_add(stats, local_stats)
            return total_T, total_E
        else:
            assert(0), "unrecognized driver & collector pair"
        #o_buf_W_T, o_buf_W_E = self.output_buf.write(vector_size * 8)
    def update(self, wr_rows, wr_cols, stats = {}):
        # driver pair: 1: ADC/DAC
        total_T = 0
        total_E = 0
        # i_buf_w_T, i_buf_w_E = self.input_buf.write(wr_rows * wr_cols * 8) # T: latency E: energy
        # total_T += i_buf_w_T
        # total_E += i_buf_w_E
        if self.driver_pair == 1:
            write_round = np.ceil(wr_rows / self.DAC_num)
            i_buf_r_T, i_buf_r_E = self.input_buf.read(self.DAC_num)
            dac_T, dac_E = self.dac.convert()
            dac_E *= self.DAC_num
            demux_T, demux_E = self.demux.execute()
            crossbar_T, crossbar_E = self.crossbar.write(self.DAC_num, wr_cols)
            # print("####################################  i_buf_r_T", i_buf_r_T, "dac_T", dac_T, "demux_T", demux_T, "crossbar_T", crossbar_T, "write_round", write_round)
            total_T = total_T + (i_buf_r_T + dac_T + demux_T + crossbar_T) * write_round
            total_E = total_E + (i_buf_r_E + dac_E + demux_E + crossbar_E) * write_round
            # print("####################################  total_T", total_T, "total_E", total_E)
            local_stats = {}
            # local_stats[self.name + "_i_buf_w_T"] = i_buf_w_T * write_round
            # local_stats[self.name + "_i_buf_w_E"] = i_buf_w_E * write_round
            local_stats[self.name + "_i_buf_r_T"] = i_buf_r_T * write_round
            local_stats[self.name + "_i_buf_r_E"] = i_buf_r_E * write_round
            local_stats[self.name + "_dac_T"] = dac_T * write_round
            local_stats[self.name + "_dac_E"] = dac_E * write_round
            local_stats[self.name + "_demux_T"] = demux_T * write_round
            local_stats[self.name + "_demux_E"] = demux_E * write_round
            local_stats[self.name + "_crossbar_T"] = crossbar_T * write_round
            local_stats[self.name + "_crossbar_E"] = crossbar_E * write_round
            merge_stats_add(stats, local_stats)
            # print("############")
            # print(stats)
            # print("############")
            return total_T, total_E
        else:
            assert(0)
    def getArea(self, stats = {}):
        if self.driver_pair == 1:
            i_buf_area = self.input_buf.getArea()
            o_buf_area = self.output_buf.getArea()
            mux_area = self.mux.getArea() * self.ADC_num
            demux_area = self.demux.getArea() * self.DAC_num
            dac_area = self.dac.getArea() * self.DAC_num
            adc_area = self.adc.getArea() * self.ADC_num
            mac_area = self.mac.getArea() * self.ADC_num
            crossbar_area = self.crossbar.getArea()
            total_area = i_buf_area + o_buf_area + mux_area + demux_area + dac_area + adc_area + mac_area + crossbar_area
            local_stats = {}
            local_stats[self.name + "_i_buf_area"] = i_buf_area
            local_stats[self.name + "_o_buf_area"] = o_buf_area
            local_stats[self.name + "_mux_area"] = mux_area
            local_stats[self.name + "_demux_area"] = demux_area
            local_stats[self.name + "_dac_area"] = dac_area
            local_stats[self.name + "_adc_area"] = adc_area
            local_stats[self.name + "_mac_area"] = mac_area
            local_stats[self.name + "_crossbar_area"] = crossbar_area
            merge_stats_add(stats, local_stats)
            return total_area
        elif self.driver_pair == 3:
            local_stats = {}
            total_area = 0
            if self.gen_PWM:
                pwm_area = self.PWM.getArea() * self.PWM_num
                total_area += pwm_area
                local_stats[self.name + "_pwm_area"] = pwm_area 
            cap_area = self.cap_ramp.getArea() * self.cap_num
            total_area += cap_area
            local_stats[self.name + "_cap_area"] = cap_area
            crossbar_area = self.crossbar.getArea()
            total_area += crossbar_area
            local_stats[self.name + "_crossbar_area"] = crossbar_area
            merge_stats_add(stats, local_stats)
            return total_area
        else:
            assert(0)