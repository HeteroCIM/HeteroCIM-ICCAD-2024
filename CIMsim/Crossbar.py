import configparser as cp
class Crossbar():
    def __init__(self, config_path = ""):
        self.RRAM_cell_type = "N/A"
        assert config_path != "", "cannot find config file!"
        self.type = type
        config = cp.ConfigParser()
        config.read(config_path)
        self.type = config["crossbar"]["type"]
        if self.type == "RRAM":
            self.RRAM_cell_type = config["crossbar"]["RRAM_cell_type"]
        self.n_rows = config.getint("crossbar", "n_rows")
        self.n_cols = config.getint("crossbar", "n_cols")
        self.bit_per_cell = config.getint("crossbar", "bit_per_cell")
        self.bit_per_weight = config.getint("crossbar", "bit_per_weight")
        self.mem_read_latency = config.getfloat("crossbar", "mem_read_latency")
        self.mem_write_latency = config.getfloat("crossbar", "mem_write_latency")
        self.mem_read_energy = config.getfloat("crossbar", "mem_read_energy")
        self.mem_write_energy = config.getfloat("crossbar", "mem_write_energy")
        self.d_weight_rows = self.n_rows # digital weight size
        self.d_weight_cols = self.n_cols # digital weight size
        if self.type == "RRAM" and self.RRAM_cell_type == "1T1R":
            # for example, 64*64 2bit 1T1R RRAM, represent 64*8 8bit number
            self.d_weight_rows = self.n_rows
            self.d_weight_cols = int(self.n_cols / (self.bit_per_weight / self.bit_per_cell * 2))
        elif self.type == "RRAM" and self.RRAM_cell_type == "2T2R":
            # for example, 64*64 2bit 2T2R RRAM, represent 32*16 8bit number
            self.d_weight_rows = int(self.n_rows / 2)
            self.d_weight_size = int(self.n_cols / (self.bit_per_weight / self.bit_per_cell))
    def compute(self, active_rows, active_cols):
        compute_latency = self.mem_read_latency
        compute_energy = self.mem_read_energy * active_rows * active_cols
        return compute_latency, compute_energy
    def update(self, active_rows, active_cols):
        update_latency = self.mem_write_latency
        update_energy = self.mem_write_energy * active_rows * active_cols
        return update_latency, update_energy