from HeteroCIM.NonlinearVecModule import *
import copy
# class evt():
#     def __init__(self, idx):
#         self.idx = idx
# a = []
# a = [evt(1), evt(2)]
# b = copy.deepcopy(a)
# c = a.copy()
# print(a)
# print(b)
# print(c)
# c.pop(0)
# print(a)
# print(b)
# print(c)
ops = (512*512*512*3 + 512*512*512 + 512*512*512 + 512*512*512 + 512*3072*512 + 3072*512*512) * 2
T = 0.019184504333333356
T_th = 0.003550280190476206
print(ops / T / 1e9)
print(ops / T_th / 1e9)
util = (3*0.0020769485238095386 + 0.003550280190476206 + 4 * 0.0029643226666666808 + 4* 0.003516413999999951)/0.003550280190476206 / 12
print("util:",util)
print(1/T_th)
print("power", 0.009007480333333326 / 0.01174588587788801)

print("-----------------------------")
T = 0.009007480333333326
T_th = 0.002438192380952381 + 0.00048444952380952383
print(ops / T / 1e9)
print(ops / T_th / 1e9)
util = (3*0.0003807778571428551 + 0.0018541095238095219 + 4 * 0.0012681519999999983 + 4* 0.0018202433333333358)/T_th / 12
print("util:",util)
print(1/T_th)
print("power", 0.013875228214911961 / 0.019184504333333356)