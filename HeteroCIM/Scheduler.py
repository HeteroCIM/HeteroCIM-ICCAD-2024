import os
import copy
from HeteroCIM.DRAM import *
from HeteroCIM.Crossbar import *
from HeteroCIM.Event import *
from HeteroCIM.EventExecutor import *
from HeteroCIM.Parser import *

class Scheduler():
    def __init__(self, event_T_E_dict):
        self.event_T_E_dict = copy.deepcopy(event_T_E_dict)
        self.scheduler_event_dict = {} # {layer_index : [events]}
    
    def remove_xbar_write(self, remove_xbar_write):
        scheduler_event_dict = {}
        for layer_idx in self.event_T_E_dict.keys():
            scheduler_event_dict[layer_idx] = []
            for event in self.event_T_E_dict[layer_idx].keys():
                if event.has_attr("is_Xbar_write") & remove_xbar_write:
                    continue
                scheduler_event_dict[layer_idx].append(event)
            # print("Remove_Xbar_Write: " + str(len(self.event_T_E_dict[layer_idx]) - len(scheduler_event_dict[layer_idx])) + " events are removed from layer " + str(layer_idx))
        return scheduler_event_dict

    def schedule_event(self, scheduler_event_dict):
        ret_dict = {} # {layer_index : {time : scheduled_list}}
        def is_ready(event, finish_id_list):
            # check data dependency
            for id in event.event_dependency:
                if id not in finish_id_list:
                    return False
            # check hardware dependency
            if event.event_type == EventType.LoadEvent or event.event_type == EventType.StoreEvent or event.event_type == EventType.MoveEvent:
                if event.dst.busy or event.src.busy:
                    return False
            elif event.event_type == EventType.CrossbarWriteEvent or event.event_type == EventType.CrossbarMultEvent or \
            event.event_type == EventType.VectorEvent or event.event_type == EventType.ReduceEvent or \
            event.event_type == EventType.CGRABatMatmulEvent or event.event_type == EventType.MergeEvent:
                if event.hardware.busy:
                    return False
            else:
                print(event)
                assert(0)
            return True
        def occupy_hardware(event):
            if event.event_type == EventType.LoadEvent or event.event_type == EventType.StoreEvent or event.event_type == EventType.MoveEvent:
                event.src.busy = True
                event.dst.busy = True
            elif event.event_type == EventType.CrossbarWriteEvent or event.event_type == EventType.CrossbarMultEvent or \
            event.event_type == EventType.VectorEvent or event.event_type == EventType.ReduceEvent or \
            event.event_type == EventType.CGRABatMatmulEvent or event.event_type == EventType.MergeEvent:
                event.hardware.busy = True
            else:
                print(event)
                assert(0)
        def release_hardware(event):
            if event.event_type == EventType.LoadEvent or event.event_type == EventType.StoreEvent or event.event_type == EventType.MoveEvent:
                event.src.busy = False
                event.dst.busy = False
            elif event.event_type == EventType.CrossbarWriteEvent or event.event_type == EventType.CrossbarMultEvent or \
            event.event_type == EventType.VectorEvent or event.event_type == EventType.ReduceEvent or \
            event.event_type == EventType.CGRABatMatmulEvent or event.event_type == EventType.MergeEvent:
                event.hardware.busy = False
            else:
                print(event)
                assert(0)
        for layer_idx in scheduler_event_dict.keys():
            wait_list = scheduler_event_dict[layer_idx].copy()
            finish_id_list = []
            sche_list = [] # on-going events: [[event, remaining_time], [...], [...]]
            sche_trace = {} # {time: [events_schedules]}
            time = 0
            sche_trace[time] = []
            test_i = 0
            while len(wait_list) != 0 or len(sche_list) != 0:
                # schedule ready events
                w_idx = 0
                for i in range(len(wait_list)):
                    event = wait_list[w_idx]
                    if is_ready(event, finish_id_list):
                        sche_list.append([event, event.get_attr("event_T")])
                        sche_trace[time].append(event)
                        occupy_hardware(event)
                        wait_list.pop(w_idx)
                    else:
                        w_idx += 1
                # time tic
                sche_list = sorted(sche_list, key=(lambda x:x[1]))
                tic = sche_list[0][1]
                time += tic
                sche_trace[time] = []
                s_idx = 0
                for i in range(len(sche_list)):
                    sche_list[s_idx][1] -= tic
                    if sche_list[s_idx][1] == 0:
                        finish_id_list.append(sche_list[s_idx][0].event_id)
                        release_hardware(sche_list[s_idx][0])
                        sche_list.pop(s_idx)
                    else:
                        s_idx += 1
            ret_dict[layer_idx] = sche_trace
        return ret_dict


                



