def merge_stats_add(dict_1, dict_2):
    dict_1_keys = dict_1.keys()
    dict_2_keys = dict_2.keys()
    for key in dict_2_keys:
        if key in dict_1_keys:
            dict_1[key] += dict_2[key]
        else:
            dict_1[key] = dict_2[key]
