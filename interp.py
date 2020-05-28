#import interface

def interp_AST(AST, env):
    atype = AST["type"]

    if atype == "Sequence":
        interp_seq(AST["seq"], env)
    else:
        raise SyntaxError("Invalid AST Type in interp_AST: " + atype)

def interp_seq(seq, env):
    for stmt in seq:
        interp_stmt(stmt, env)

def interp_stmt(stmt, env):
    stype = stmt["type"]

    if stype == "Action":
        interp_action(stmt["action"], env)
    else:
        raise SyntaxError("Invalid AST Type in interp_stmt: " + stype)

def interp_action(action, env):
    atype = action["type"]

    if atype == "Print":
        print(interp_atom(action["args"], env))
    elif atype == "Set":
        env[action["args"][0]] = interp_atom(action["args"][1], env)
    elif atype == "Add" or atype == "Sub" or atype == "Mul" or atype == "Div":
        env[action["args"][0]] = bin_op(interp_atom(action["args"][1], env), interp_atom(action["args"][2], env), atype)
    else: 
        raise SyntaxError("Invalid AST Type in interp_action: " + atype)

def interp_atom(atom, env):
    if atom == "" or atom is None:
        raise SyntaxError("Missing arg or empty arg in interp_atom")

    if atom[0] == "&":
        return env[atom[1:]]
    else:
        return atom
    """
    elif atom[0] == "#":
        exec("global res; res = %s" % atom[1:])
        global res
        return str(res)
    """

def bin_op(a, b, op):
    if op == "Add":
        return str(int(a) + int(b))
    elif op == "Sub":
        return str(int(a) - int(b))
    elif op == "Mul":
        return str(int(a) * int(b))
    elif op == "Div":
        return str(int(a) / int(b))
