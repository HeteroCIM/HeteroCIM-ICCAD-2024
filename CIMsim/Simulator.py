import os
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.EventExecutor import *
from CIMsim.Parser import *
from CIMsim.utils import event_to_string
from CIMsim.Scheduler import *

class Simulator():
    def __init__(self, tile_config_path = "", DRAM_config_path = "", FPGA_config_path = "", protocol_config_path = "", nvm_config_path = ""):
        self.tile_config_path = tile_config_path
        self.DRAM_config_path = DRAM_config_path
        self.FPGA_config_path = FPGA_config_path
        self.protocol_config_path = protocol_config_path
        self.nvm_config_path = nvm_config_path
        self.hardware_dict = {}
        self.parser_res_dict = {} # {layer_idx: {event: tuple(T, E, stats)}}
        self.parser_stats_dict = {}

    def add_protocol(self):
        assert self.protocol_config_path != "", "cannot find protocol config file!"
        config = cp.ConfigParser()
        config.read(self.protocol_config_path)
        if config["Protocol"]["inter_chip_connection"] == "PCIe":
            pcie = PCIe("PCIe", self.protocol_config_path)
            self.hardware_dict["inter_chip_connection"] = pcie
        else:
            assert(0 and "unsupported protocol")

    def parse_json(self, filename):
        ps = Parser(self.tile_config_path, self.DRAM_config_path, self.FPGA_config_path)
        ps.tile_NVM_config_path = self.nvm_config_path
        self.event_list_dict = ps.parse_linecode_file(filename)
        self.hardware_dict.update(ps.get_hardware_dict())
        # for event in self.event_list:
        #     print(event_to_string(event))
        for hardware_name in self.hardware_dict.keys():
            print(self.hardware_dict[hardware_name].name)
    
    def execute_event(self):
        ex = eventExecuter(self.hardware_dict)
        for layer_idx in self.event_list_dict.keys():
            self.parser_res_dict[layer_idx] = ex.execute_events(self.event_list_dict[layer_idx])
            for event in self.event_list_dict[layer_idx]:
                res_tuple = self.parser_res_dict[layer_idx][event]
                event_T = res_tuple[0]
                event_E = res_tuple[1]
                stats = res_tuple[2]
                event.set_attr("event_T", event_T)
                event.set_attr("event_E", event_E)
                event.set_attr("event_stats", stats)
            # print("event:", event.event_name, "latency:", event_T, "energy", event_E)
    def print_simulation_result(self, filename):
        textfile = open(filename,'w',encoding="utf-8")
        for layer_idx in self.event_list_dict.keys():
            for event in self.event_list_dict[layer_idx]:
                # content = "layer_idx: " + str(layer_idx) + " event: " + event.event_name + " event_T: " + str(event.get_attr("event_T")) + " event_E: " + str(event.get_attr("event_E"))
                content = f"{'layer_idx: ' + str(layer_idx) :<15}" + f"{'event_idx: ' + str(event.event_id) :<30}"  + f"{'event: ' + event.event_name :<40}" + f"{'event_T: ' + str(event.get_attr('event_T')) :<40}" + f"{'event_E: ' + str(event.get_attr('event_E')) :<50}"
                print(content, event.get_attr("event_stats"), file=textfile)
    def print_event_list(self, filename):
        textfile = open(filename,'w',encoding="utf-8")
        for layer_idx in self.event_list_dict.keys():
            for event in self.event_list_dict[layer_idx]:
                # content = "layer_idx: " + str(layer_idx) + " event: " + event.event_name + " event_T: " + str(event.get_attr("event_T")) + " event_E: " + str(event.get_attr("event_E"))
                if (event is None):
                    print(layer_idx, event)
                    assert(0)
                content = f"{'layer_idx: ' + str(layer_idx) :<15}" + f"{'event_idx: ' + str(event.event_id) :<30}" + f"{'event: ' + event.event_name :<40}"
                print(content, file=textfile)

    def get_stats_from_res(self, res_dict):
        stats_dict = {}
        for layer_idx in res_dict.keys():
            layer_T = 0
            layer_E = 0
            for event in res_dict[layer_idx]:
                layer_T += event.get_attr("event_T")
                layer_E += event.get_attr("event_E")
            stats_dict[layer_idx] = [layer_T, layer_E]
        return stats_dict

    def print_stats(self, dict, filename = ""):
        if filename != "":
            textfile = open(filename,'w',encoding="utf-8")
        for layer_idx in dict.keys():
            T = dict[layer_idx][0]
            E = dict[layer_idx][1]
            content = f"{'layer_idx: ' + str(layer_idx) :<15}" + f"{'event_T: ' + str(T) :<40}" + f"{'event_E: ' + str(E) :<40}"
            if filename == "":
                print(content)
            else:
                print(content, textfile)
            
    def print_sche_trace(self, dict, filename = ""):
        assert(filename != "")
        textfile = open(filename,'w',encoding="utf-8")
        for layer_idx in dict.keys():
            print("---------------------------------layer" + str(layer_idx) + "---------------------------------", file=textfile)
            for time in dict[layer_idx].keys():
                time_str = f"{'time: ' + str(time) :<30}"
                content = time_str
                for event in dict[layer_idx][time]:
                    content += f"{'event_' + str(event.event_id) + ': ' + event.event_name:<40}"
                # print(content, file=textfile)

    def get_latency_from_trace(self, trace):
        ret_dict = {}
        for layer_idx in trace.keys():
            layer_trace = trace[layer_idx]
            layer_time = list(layer_trace.keys())[-1]
            ret_dict[layer_idx] = layer_time
        return ret_dict

    def schedule(self):
        print("-----------start scheduling------------")
        sc = Scheduler(self.parser_res_dict)
        scheduler_event_dict = sc.remove_xbar_write()
        remove_stats_dict = self.get_stats_from_res(scheduler_event_dict)
        print("stats after removing xbar writes:")
        self.print_stats(remove_stats_dict)
        self.event_list_dict = scheduler_event_dict
        sche_trace = sc.schedule_event(self.event_list_dict)
        self.print_sche_trace(sche_trace, "sche_trace.txt")
        sche_latency_dict = self.get_latency_from_trace(sche_trace)
        print("sche_latency_dict:")
        print(sche_latency_dict)
        sche_stats_dict = copy.deepcopy(remove_stats_dict)
        for layer_idx in sche_latency_dict.keys():
            sche_stats_dict[layer_idx][0] = sche_latency_dict[layer_idx]
        print("stats after scheduling:")
        self.print_stats(sche_stats_dict)

