from CIMsim.NonlinearVecModule import *
nvm = NonlinearVecModule("nvm.ini")
# for i in nvm.activaton_module_dict.keys():
#     print(i, nvm.activaton_module_dict[i].n_samples)
T, E = nvm.compute("activation", "GeLU")
print(T, E)