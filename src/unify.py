class Ref:
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        if not isinstance(other, Ref):
            return False
        return self.name == other.name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

class Func:
    def __init__(self, name, *elems):
        self.name = name
        self.elems = list(elems)

    def __eq__(self, other):
        if not isinstance(other, Func):
            return False
        if self.name != other.name:
            return False
        if len(self.elems) != len(other.elems):
            return False
        return all(i == j for i, j in zip(self.elems, other.elems))

    def eq_toplevel(self, other):
        return isinstance(other, Func) and self.name == other.name and len(self.elems) == len(other.elems)

    def contains_ref(self, ref):
        for elem in self.elems:
            if isinstance(elem, Func):
                if elem.contains_ref(ref):
                    return True
            else:
                if ref == elem:
                    return True
        return False

    def replace_ref(self, ref, repl):
        for i, elem in enumerate(self.elems):
            if isinstance(elem, Func):
                elem.replace_ref(ref, repl)
            elif ref == elem:
                self.elems[i] = repl

    def __str__(self):
        s = str(self.name) + "("
        for i, elem in enumerate(self.elems):
            s += str(elem)
            if i < len(self.elems) - 1:
                s += ", "
            else:
                s += ")"
        return s

    def __repr__(self): # str([Func("f")]) calls repr for some reason
        return str(self)

class UnificationError(Exception):
    def __init__(self, left, right):
        super().__init__(repr(left) + " -> " + repr(right))

def robinson(eqts):
    maps = []

    while eqts:
        left, right = eqts[0]
        eqts = eqts[1:]
        if left == right:
            continue
        if isinstance(left, Ref) and not (isinstance(right, Func) and right.contains_ref(left)):
            maps.append([left, right])
            for i, (el, er) in enumerate(eqts):
                if isinstance(el, Func): el.replace_ref(left, right)
                elif left == el: eqts[i][0] = right
                if isinstance(er, Func): er.replace_ref(left, right)
                elif left == er: eqts[i][1] = right
        elif isinstance(right, Ref) and not (isinstance(left, Func) and left.contains_ref(right)):
            maps.append([right, left])
            for i, (el, er) in enumerate(eqts):
                if isinstance(el, Func): el.replace_ref(right, left)
                elif right == el: eqts[i][0] = left
                if isinstance(er, Func): er.replace_ref(right, left)
                elif right == er: eqts[i][1] = left
        elif isinstance(left, Func) and left.eq_toplevel(right):
            eqts.extend(list(z) for z in zip(left.elems, right.elems))
        else:
            raise UnificationError(left, right)

    # apply each map in reverse order
    for i in range(len(maps) - 1, -1, -1):
        curr_lhs, curr_rhs = maps[i]
        for j in range(i):
            rhs = maps[j][1]
            if isinstance(rhs, Func):
                rhs.replace_ref(curr_lhs, curr_rhs)
            elif curr_lhs == rhs:
                maps[j][1] = curr_rhs

    return maps

if __name__ == "__main__":
    def exponential(n):
        left = Func("f", *(Ref("X" + str(i)) for i in range(1, n + 1)))
        right = Func("f", *(Func("g", Ref("X" + str(i)), Ref("X" + str(i))) for i in range(n)))
        return [[left, right]]
    eqts = exponential(3)
    print(eqts[0][0])
    print(eqts[0][1])
    print(robinson(exponential(3)))
