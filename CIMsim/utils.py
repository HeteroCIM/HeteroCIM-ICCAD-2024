from typing import List

def merge_stats_add(dict_1, dict_2):
    dict_1_keys = dict_1.keys()
    dict_2_keys = dict_2.keys()
    for key in dict_2_keys:
        if key in dict_1_keys:
            dict_1[key] += dict_2[key]
        else:
            dict_1[key] = dict_2[key]
    return
    
def get_detailed_stats(total_stats, module_dicts: List[dict], module_names: List[str], stat_names: List[str]):
    assert len(module_dicts) == len(module_names)
    ret_dict = {}
    ratio_dict = {}
    for stat_name in stat_names:
        stat = 0
        for i in range(len(module_names)):
            stat_key = module_names[i] + "_" + stat_name
            stat += module_dicts[i][stat_key]
        ret_dict[stat_name] = stat
        ratio_dict[stat_name] = stat / total_stats * 100
    return ret_dict, ratio_dict

# def event_scheduler(event_PP_dict):
#     cycle = 0

def event_to_string(event):
    from CIMsim.Event import EventType
    def event_type_to_string(event_type):
        event_type_to_string_dict = {
            EventType.CrossbarMultEvent: "CrossbarMultEvent",
            EventType.LoadEvent: "LoadEvent",
            EventType.StoreEvent: "StoreEvent",
            EventType.MoveEvent: "MoveEvent",
            EventType.CrossbarWriteEvent: "CrossbarWriteEvent",
            EventType.ActivationEvent: "ActivationEvent",
            EventType.VectorEvent: "VectorEvent",
            EventType.ReduceEvent: "ReduceEvent",
            EventType.FPGABatMatmulEvent: "FPGABatMatmulEvent",
            EventType.MergeEvent: "MergeEvent"
        }
        return event_type_to_string_dict[event_type]
    str_type = event_type_to_string(event.event_type)
    str_id = event.event_id
    str_name = event.event_name
    str_event = "event_id: " + str(str_id) + "  event_name: " + str_name + "  event_type: " + str_type
    return str_event
