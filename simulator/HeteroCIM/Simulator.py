import os
from HeteroCIM.DRAM import *
from HeteroCIM.Crossbar import *
from HeteroCIM.Event import *
from HeteroCIM.EventExecutor import *
from HeteroCIM.Parser import *
from HeteroCIM.Scheduler import *

class Simulator():
    def __init__(self, tile_config_path = "", DRAM_config_path = "", CGRA_config_path = "", protocol_config_path = "", nvm_config_path = ""):
        self.tile_config_path = tile_config_path
        self.DRAM_config_path = DRAM_config_path
        self.CGRA_config_path = CGRA_config_path
        self.protocol_config_path = protocol_config_path
        self.nvm_config_path = nvm_config_path
        self.hardware_dict = {}
        self.event_T_E_dict = {} # {layer_idx: {event: tuple(T, E, stats)}}
        self.parser_stats_dict = {}
        self.sched_layer_T_E_dict = {}
        self.scheduler = None
    
    def get_CIM_tile_area(self):
        area_dict = {}
        for key in self.hardware_dict.keys():
            hardware = self.hardware_dict[key]
            if isinstance(hardware, Tile):
                area_dict[hardware] = hardware.getArea()

    def build_inter_die_protocol(self):
        assert self.protocol_config_path != "", "cannot find protocol config file!"
        config = cp.ConfigParser()
        config.read(self.protocol_config_path)
        if config["Protocol"]["inter_die_connection"] == "PCIe":
            pcie = PCIe("PCIe", self.protocol_config_path)
            self.hardware_dict["inter_die_connection"] = pcie
        elif config["Protocol"]["inter_die_connection"] == "UCIe":
            ucie = UCIe("UCIe", self.protocol_config_path)
            self.hardware_dict["inter_die_connection"] = ucie
        elif config["Protocol"]["inter_die_connection"] == "CXL":
            cxl = CXL("CXL", self.protocol_config_path)
            self.hardware_dict["inter_die_connection"] = cxl
        else:
            assert(0 and "unsupported protocol")

    def parse_json(self, filename):
        ps = Parser(self.tile_config_path, self.DRAM_config_path, self.CGRA_config_path)
        ps.tile_NVM_config_path = self.nvm_config_path 
        self.event_list_dict = ps.parse_linecode_file(filename)
        self.hardware_dict.update(ps.get_hardware_dict())
        for hardware_name in self.hardware_dict.keys():
            print(self.hardware_dict[hardware_name].name)
    
    def execute_event(self):
        ex = eventExecuter(self.hardware_dict)
        for layer_idx in self.event_list_dict.keys():
            self.event_T_E_dict[layer_idx] = ex.execute_events(self.event_list_dict[layer_idx])
            for event in self.event_list_dict[layer_idx]:
                res_tuple = self.event_T_E_dict[layer_idx][event]
                event_T = res_tuple[0]
                event_E = res_tuple[1]
                stats = res_tuple[2]
                event.set_attr("event_T", event_T)
                event.set_attr("event_E", event_E)
                event.set_attr("event_stats", stats)

    def print_event_T_E(self, filename):
        textfile = open(filename,'w',encoding="utf-8")
        for layer_idx in self.event_list_dict.keys():
            for event in self.event_list_dict[layer_idx]:
                content = f"{'layer_idx: ' + str(layer_idx) :<15}" + f"{'event_idx: ' + str(event.event_id) :<30}"  + f"{'event: ' + event.event_name :<40}" + f"{'event_T: ' + str(event.get_attr('event_T')) :<40}" + f"{'event_E: ' + str(event.get_attr('event_E')) :<50}"
                print(content, event.get_attr("event_stats"), file=textfile)

    def print_event_list(self, filename):
        textfile = open(filename,'w',encoding="utf-8")
        for layer_idx in self.event_list_dict.keys():
            for event in self.event_list_dict[layer_idx]:
                content = f"{'layer_idx: ' + str(layer_idx) :<15}" + f"{'event_idx: ' + str(event.event_id) :<30}" + f"{'event: ' + event.event_name :<40}"
                print(content, file=textfile)

    def get_raw_layer_T_E(self, res_dict):
        layer_T_E_dict = {}
        for layer_idx in res_dict.keys():
            layer_T = 0
            layer_E = 0
            for event in res_dict[layer_idx]:
                layer_T += event.get_attr("event_T")
                layer_E += event.get_attr("event_E")
            layer_T_E_dict[layer_idx] = [layer_T, layer_E]
        return layer_T_E_dict

    def print_layer_T_E(self, dict, file_path = None):
        if file_path is not None:
            textfile = open(file_path,'w',encoding="utf-8")
        total_T = 0
        total_E = 0
        for layer_idx in dict.keys():
            T = dict[layer_idx][0]
            E = dict[layer_idx][1]
            total_T += T
            total_E += E
            content = f"{'layer_idx: ' + str(layer_idx) :<15}" + f"{'event_T: ' + str(T) :<40}" + f"{'event_E: ' + str(E) :<40}"
            if file_path is None:
                print(content) 
            else:
                print(content, textfile)
        print("total_T: ", total_T, "total_E: ", total_E)

    def schedule(self, trace_output_path = "outputs/sche_trace.txt", remove_xbar_write = True):
        self.scheduler = Scheduler(self.event_T_E_dict)
        scheduler_event_dict = self.scheduler.remove_xbar_write(remove_xbar_write)
        raw_layer_T_E_dict = self.get_raw_layer_T_E(scheduler_event_dict)
        self.event_list_dict = scheduler_event_dict
        sche_trace = self.scheduler.schedule_event(self.event_list_dict)
        self.print_sche_trace(sche_trace, trace_output_path)
        sche_latency_dict = self.get_latency_from_trace(sche_trace)
        sched_layer_T_E_dict = copy.deepcopy(raw_layer_T_E_dict)
        for layer_idx in sche_latency_dict.keys():
            sched_layer_T_E_dict[layer_idx][0] = sche_latency_dict[layer_idx]
        self.sched_layer_T_E_dict = sched_layer_T_E_dict

    def print_sche_trace(self, dict, file_path = None):
        assert(file_path is not None)
        textfile = open(file_path,'w',encoding="utf-8")
        for layer_idx in dict.keys():
            print("layer_" + str(layer_idx) + ":", file=textfile)
            for time in dict[layer_idx].keys():
                time_str = f"{'time: ' + str(time) :<30}"
                content = time_str
                for event in dict[layer_idx][time]:
                    content += f"{'event_' + str(event.event_id) + ': ' + event.event_name:<40}"
                print(content, file=textfile)

    def get_latency_from_trace(self, trace):
        ret_dict = {}
        for layer_idx in trace.keys():
            layer_trace = trace[layer_idx]
            layer_time = list(layer_trace.keys())[-1]
            ret_dict[layer_idx] = layer_time
        return ret_dict

