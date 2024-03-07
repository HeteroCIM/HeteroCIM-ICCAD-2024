class father():
    def __init__(self, name):
        self.a = 1
        self.b = name

class son(father):
    def __init__(self, name):
        super().__init__(name)
        self.c = 2

# s = son("hi")
# print(s.a)
