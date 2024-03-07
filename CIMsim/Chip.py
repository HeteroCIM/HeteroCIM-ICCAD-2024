import configparser as cp
class Chip():
    def __init__(self, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.tile_num = config.getfloat("chip", "tile_num")
        self.tile_connection = config.getfloat("chip", "tile_connection")
    def compute(self, event):
        pass