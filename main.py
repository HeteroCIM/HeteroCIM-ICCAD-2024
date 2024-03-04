import os
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
crossbar = Crossbar("config.ini")
print(crossbar.compute(64,64))

dram = DRAM("config.ini")
print(dram.size)