import configparser as cp
class ADC():
    def __init__(self, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.precision = config.getint("ADC", "precision")
        sample_rate = config.getfloat("ADC", "sample_rate")
        if config.getfloat("ADC", "latency") != -1:
            self.convert_latency = config.getfloat("ADC", "latency")
        else:
            self.convert_latency = 1 / sample_rate * (self.precision + 2)

        self.power = config.getfloat("ADC", "power")
        self.area = config.getfloat("ADC", "area")
        if (sample_rate == -1):
            match self.precision:
                case 1:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC sample rate in config file"
                case 2:
                    # assert(0), "No default configs for selected ADC bits. Please enter ADC sample rate in config file"
                    sample_rate = 1e9
                case 3:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC sample rate in config file"
                case 4:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC sample rate in config file"
                case 5:
                    sample_rate = 12e9 # A_12-GS_s_81-mW_5-bit_Time-Interleaved_Flash_ADC_With_Background_Timing_Skew_Calibration
                case 6: 
                    sample_rate = 1e9 # Area-Efficient 1GS/s 6b SAR ADC with Charge Injection-Cell-Based DAC
                case 7:
                    sample_rate = 2.4e9 # A two-way interleaved 7-b 2.4-GS/s 1-then-2 b/cycle SAR ADC with background offset calibration
                case 8:
                    sample_rate = 1.2e9 # ISAAC: A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars
        if (self.power == -1):
            match self.precision:
                case 1:
                    # assert(0), "No default configs for selected ADC bits. Please enter ADC power in config file"
                    self.power = 0.004 * 2 ** self.precision
                case 2:
                    # assert(0), "No default configs for selected ADC bits. Please enter ADC power in config file"
                    self.power = 0.004 * 2 ** self.precision
                case 3:
                    # assert(0), "No default configs for selected ADC bits. Please enter ADC power in config file"
                    self.power = 0.004 * 2 ** self.precision
                case 4:
                    # assert(0), "No default configs for selected ADC bits. Please enter ADC power in config file"
                    self.power = 0.004 * 2 ** self.precision
                case 5: 
                    self.power = 0.081 # A_12-GS_s_81-mW_5-bit_Time-Interleaved_Flash_ADC_With_Background_Timing_Skew_Calibration
                case 6:
                    self.power = 1.26e-3 # Area-Efficient 1GS/s 6b SAR ADC with Charge Injection-Cell-Based DAC
                case 7:
                    self.power = 5e-3 # A two-way interleaved 7-b 2.4-GS/s 1-then-2 b/cycle SAR ADC with background offset calibration
                case 8:
                    self.power = 16e-3 # ISAAC: A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars
        if (self.area == -1):
            match self.precision:
                case 1:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC area in config file"
                case 2:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC area in config file"
                case 3:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC area in config file"
                case 4:
                    assert(0), "No default configs for selected ADC bits. Please enter ADC area in config file"
                case 5:
                    self.area = 4400 # A_12-GS_s_81-mW_5-bit_Time-Interleaved_Flash_ADC_With_Background_Timing_Skew_Calibration
                case 6:
                    self.area = 580 # Area-Efficient 1GS/s 6b SAR ADC with Charge Injection-Cell-Based DAC
                case 7:
                    self.area = 4300 # A two-way interleaved 7-b 2.4-GS/s 1-then-2 b/cycle SAR ADC with background offset calibration
                case 8:
                    self.area = 9600 # ISAAC: A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars


        if config.getfloat("ADC", "latency") != -1:
            self.convert_latency = config.getfloat("ADC", "latency")
        else:
            self.convert_latency = 1 / sample_rate * (self.precision + 2)
        self.convert_energy = self.convert_latency * self.power
        # default config comes from "ISAAC: A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars"
        self.convert_energy = self.convert_latency * self.power
    def convert(self):
        return self.convert_latency, self.convert_energy
    def getArea(self):
        # print(self.area)
        return self.area

# collect output results with capacitor and ramp circuit
class CapRamp():
    def __init__(self, config_path = ""):
        assert config_path != "", "cannot find config file!"
        config = cp.ConfigParser()
        config.read(config_path)
        self.precision = config.getint("CapRamp", "precision")
        self.tick = config.getfloat("CapRamp", "tick")
        self.area = config.getfloat("CapRamp", "area")
        self.power = config.getfloat("CapRamp", "power")
        self.latency = 2 ** self.precision * self.tick
        self.energy = self.power * self.latency
    def convert(self):
        return self.latency, self.energy
    def getArea(self):
        return self.area
