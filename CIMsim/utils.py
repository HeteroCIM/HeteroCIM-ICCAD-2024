from typing import List
def merge_stats_add(dict_1, dict_2):
    dict_1_keys = dict_1.keys()
    dict_2_keys = dict_2.keys()
    for key in dict_2_keys:
        if key in dict_1_keys:
            dict_1[key] += dict_2[key]
        else:
            dict_1[key] = dict_2[key]

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

def event_scheduler(event_PP_dict):
    cycle = 0
    