from CIMsim.NonlinearVecModule import *
import copy
class evt():
    def __init__(self, idx):
        self.idx = idx
a = []
a = [evt(1), evt(2)]
b = copy.deepcopy(a)
c = a.copy()
print(a)
print(b)
print(c)
c.pop(0)
print(a)
print(b)
print(c)