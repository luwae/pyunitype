from unify import Ref, Func, UnificationError, robinson

class OutOfScopeError(Exception):
    def __init__(self, name):
        super().__init__(f"object {name} not in scope")

class Const:
    def __init__(self, val, tp):
        self.var = val
        self.tp = tp
    def infer(self, typevar, gamma, constraints, ngen):
        constraints.append([typevar, self.tp])

class Var:
    def __init__(self, name):
        self.name = name
    def infer(self, typevar, gamma, constraints, ngen):
        try:
            constraints.append([typevar, gamma[self.name]])
        except KeyError as e:
            raise OutOfScopeError(e)

class App:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
    def infer(self, typevar, gamma, constraints, ngen):
        v1 = next(ngen)
        v2 = next(ngen)
        constraints.append([v1, Func("->", v2, typevar)])
        self.func.infer(v1, gamma, constraints, ngen)
        self.arg.infer(v2, gamma, constraints, ngen)

class Abs:
    def __init__(self, var, arg):
        self.var = var
        self.arg = arg
    def infer(self, typevar, gamma, constraints, ngen):
        v1 = next(ngen)
        v2 = next(ngen)
        constraints.append([typevar, Func("->", v1, v2)])
        gamma[self.var] = v1
        self.arg.infer(v2, gamma, constraints, ngen)

def vargen():
    i = 1
    while True:
        yield Ref(f"a{i}")
        i += 1

# z :: int -> int
# \y. \x. y 7 z
c = Abs("y", Abs("x", App(App(Var("y"), Const(7, "int")), Var("z"))))
# c = Abs("x", Abs("y", App(App(Var("y"), Var("x")), Var("x"))))
v = vargen()
gamma = {"z" : Func("->", "int", "int")}
constraints = []
c.infer(next(v), gamma, constraints, v)
print(gamma)
print(constraints)
res = robinson(constraints)
print(res)

def str_infix(arg):
    if isinstance(arg, Func):
        if len(arg.elems) != 2:
            raise ValueError("invalid number of arguments for infix operator")
        return f"({str_infix(arg.elems[0])} {arg.name} {str_infix(arg.elems[1])})"
    return str(arg)

print("type:", str_infix(res[0][1]))
