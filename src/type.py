from unify import Ref, Func, UnificationError, robinson

class Const:
    def __init__(self, val, tp):
        self.var = val
        self.tp = tp
    def work(self, typevar, gamma, constraints, ngen):
        constraints.append([typevar, self.tp])

class Var:
    def __init__(self, name):
        self.name = name
    def work(self, typevar, gamma, constraints, ngen):
        constraints.append([typevar, gamma[self.name]])

class App:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
    def work(self, typevar, gamma, constraints, ngen):
        v1 = next(ngen)
        v2 = next(ngen)
        constraints.append([v1, Func("->", v2, typevar)])
        self.func.work(v1, gamma, constraints, ngen)
        self.arg.work(v2, gamma, constraints, ngen)

class Abs:
    def __init__(self, var, arg):
        self.var = var
        self.arg = arg
    def work(self, typevar, gamma, constraints, ngen):
        v1 = next(ngen)
        v2 = next(ngen)
        constraints.append([typevar, Func("->", v1, v2)])
        gamma[self.var] = v1
        self.arg.work(v2, gamma, constraints, ngen)

def vargen():
    i = 1
    while True:
        yield Ref(f"a{i}")
        i += 1

# \y. y y
c = Abs("y", App(Var("y"), Var("y")))
# c = Abs("x", Abs("y", App(App(Var("y"), Var("x")), Var("x"))))
v = vargen()
gamma = {}
constraints = []
c.work(next(v), gamma, constraints, v)
print(gamma)
print(constraints)
print(robinson(constraints))

# \f. (\x. (((f x) x) 5))
# Abs("f", Abs("x", App(App(App(Var("f"), Var("x")), Var("x")), Const(5, "int")))
