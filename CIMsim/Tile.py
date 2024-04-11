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
from CIMsim.NonlinearVecModule import *
import numpy as np

# a crossbar array tile
class Tile(): 
    def __init__(self, name, config_path = "", nvm_path = ""):
        config = cp.ConfigParser()
        config.read(config_path)
        assert config_path != "", "cannot find config file!"
        self.name = name
        self.PE_num = config.getint("Tile", "PE_num")
        self.has_ReLU = config.getboolean("Tile", "has_ReLU")
        self.tile_in_buf = Buffer(self.name + "_tile_in_buf", config_path, "Tile Input Buffer")
        self.tile_out_buf = Buffer(self.name + "_tile_out_buf", config_path, "Tile Output Buffer")
        self.PEs = []
        for i in range(self.PE_num):
            self.PEs.append(PE(self.name + "_PE_" + str(i), config_path))
        self.nvm_path = nvm_path
        if nvm_path != "":
            self.nonlinear_vec_module = NonlinearVecModule(name = "nvm", config_path = nvm_path)
        else:
            assert(0), "for now each tile should have NVM module"
        self.merge_unit = MAC(config_path)
    def getArea(self, stats={}):
        PE_area = 0
        for pe in self.PEs:
            PE_area += pe.getArea()
        buf_area = self.tile_in_buf.getArea() + self.tile_out_buf.getArea()
        total_area = PE_area + buf_area # TODO: +++++
        return total_area
