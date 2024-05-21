import configparser as cp
class Crossbar():
    def __init__(self, config_path = ""):
        self.RRAM_cell_type = "N/A"
        assert config_path != "", "cannot find config file!"
        self.type = type
        config = cp.ConfigParser()
        config.read(config_path)
        self.cb = None
        self.type = config["crossbar"]["type"]
        if self.type == "ACIM":
            self.cb = ACIM(config_path) 
            self.type = config["crossbar"]["mem_type"]
        elif self.type == "DCIM":
            self.cb = DCIM(config_path)
        else:
            assert(0)
    def compute(self, active_rows, active_cols):
        return self.cb.compute(active_rows, active_cols)
    def write(self, active_rows, active_cols):
        return self.cb.write(active_rows, active_cols)
    def getArea(self):
        return self.cb.getArea()
        
class ACIM():
    def __init__(self, config_path = ""):
        self.RRAM_cell_type = "N/A"
        assert config_path != "", "cannot find config file!"
        self.type = type
        config = cp.ConfigParser()
        config.read(config_path)
        self.n_rows = config.getint("crossbar", "n_rows")
        self.n_cols = config.getint("crossbar", "n_cols")
        self.mem_bits = config.getint("crossbar", "mem_bits")
        self.weight_bits = config.getint("crossbar", "weight_bits")
        self.mem_write_latency = config.getfloat("crossbar", "mem_write_latency")
        self.mem_write_energy = config.getfloat("crossbar", "mem_write_energy")
        self.cell_area = config.getfloat("crossbar", "cell_area")
        self.busy = False

        self.type = config["crossbar"]["mem_type"]
        if self.type == "RRAM":
            self.RRAM_cell_type = config["crossbar"]["RRAM_cell_type"]
            self.SA_latency = config.getfloat("crossbar", "SA_latency") if config.getfloat("crossbar", "SA_latency") != -1 else 50e-9
            self.SA_energy = config.getfloat("crossbar", "SA_energy") if config.getfloat("crossbar", "SA_energy") != -1 else 50e-6 * 50e-9
            if self.RRAM_cell_type == "1T1R":
                # for example, 64*64 2bit 1T1R RRAM, represent 64*8 8bit number
                self.d_weight_rows = self.n_rows
                self.d_weight_cols = int(self.n_cols / (self.weight_bits / self.mem_bits) / 2)
            elif self.RRAM_cell_type == "2T2R":
                # for example, 64*64 2bit 2T2R RRAM, represent 32*16 8bit number
                self.d_weight_rows = int(self.n_rows)
                self.d_weight_cols = int(self.n_cols / (self.weight_bits / self.mem_bits))
            else:
                assert(0), "Only support 1T1R and 2T2R for RRAM configs now."
        elif self.type == "PCM":
            # assume 1T1R
            self.d_weight_rows = int(self.n_rows)
            self.d_weight_cols = int(self.n_cols / (self.weight_bits / self.mem_bits) / 2)
    def compute(self, active_rows, active_cols):
        compute_latency = self.SA_latency
        compute_energy = self.SA_energy * active_cols
        return compute_latency, compute_energy
    def write(self, active_rows, active_cols):
        update_latency = self.mem_write_latency
        update_energy = self.mem_write_energy * active_rows * active_cols
        return update_latency, update_energy
    def getArea(self):
        if self.cell_area == -1:
            if self.type == "RRAM":
                self.transistor_area = 0.0046 # TODO: different technology nodes
                self.rram_area =  0.0121
                if self.RRAM_cell_type == "1T1R":
                    self.cell_area = self.rram_area + self.transistor_area
                elif self.RRAM_cell_type == "2T2R":
                    self.cell_area = (self.rram_area + self.transistor_area) * 2
                else: 
                    print(self.type, self.RRAM_cell_type)
                    assert(0)
            elif self.type == "PCM":
                self.cell_area = 0.2025 # A_90nm_32-mb_phase_change_memory_with_flash_SPI_compatibility
                self.transistor_area = 0.0046
                self.cell_area += self.transistor_area
        area = self.cell_area * self.n_rows * self.n_cols
        return area


class DCIM():
    def __init__(self, config_path = ""):
        self.RRAM_cell_type = "N/A"
        assert config_path != "", "cannot find config file!"
        self.type = type
        config = cp.ConfigParser()
        config.read(config_path)
        self.n_rows = config.getint("crossbar", "n_rows")
        self.n_cols = config.getint("crossbar", "n_cols")
        self.weight_bits = config.getint("crossbar", "weight_bits")
        self.input_bits = config.getint("crossbar", "input_bits")
        self.frequency = config.getfloat("crossbar", "frequency")
        self.mem_read_latency = config.getfloat("crossbar", "mem_read_latency") * 1 / self.frequency
        self.mem_write_latency = config.getfloat("crossbar", "mem_write_latency")
        self.mem_read_energy = config.getfloat("crossbar", "mem_read_energy")
        self.mem_write_energy = config.getfloat("crossbar", "mem_write_energy")
        self.logic_gate_energy = config.getfloat("crossbar", "logic_gate_energy")
        self.adder_energy = config.getfloat("crossbar", "adder_energy")
        self.cell_area = config.getfloat("crossbar", "cell_area")
        self.busy = False

    def compute(self, rows, cols):
        assert(rows == 1)
        compute_latency = self.mem_read_latency * rows * self.input_bits
        compute_energy = (self.mem_read_energy + self.logic_gate_energy + self.adder_energy) * rows * cols * self.input_bits
        return compute_latency, compute_energy
    def write(self, active_rows, active_cols):
        # need mux, DAC, xxx latency & energy
        update_latency = self.mem_write_latency
        update_energy = self.mem_write_energy * active_rows * active_cols
        return update_latency, update_energy
    def getArea(self):
        if self.cell_area == -1:
            if self.type == "RRAM":
                self.transistor_area = 0.0046 # TODO: different technology nodes
                self.rram_area =  0.0121
                if self.RRAM_cell_type == "1T1R":
                    self.cell_area = self.rram_area + self.transistor_area
                elif self.RRAM_cell_type == "2T2R":
                    self.cell_area = (self.rram_area + self.transistor_area) * 2
                else: 
                    print(self.type, self.RRAM_cell_type)
                    assert(0)
            elif self.type == "PCM":
                self.cell_area = 0.2025 # A_90nm_32-mb_phase_change_memory_with_flash_SPI_compatibility
                self.transistor_area = 0.0046
                self.cell_area += self.transistor_area
        area = self.cell_area * self.n_rows * self.n_cols
        return area