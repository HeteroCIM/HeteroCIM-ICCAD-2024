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
from CIMsim.PE import *
class FPGA():
    def __init__(self, name, config_path = "") -> None:
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        type = config["FPGA"]["type"]
        if type == "OPU":
            self.name = name
            self.hardware = OPU()
        else:
            assert(0), "For now, we only support coarse-grained OPU model for FPGA config"
        self.FPGA_buf = Buffer(self.name + "_FPGA_buf", config_path, "FPGA Buffer")
        self.NVM_reg = Buffer(self.name + "_NVM_vreg", config_path, "NVM VREG")

class OPU():
    # paper cited
    def __init__(self) -> None:
        pass
