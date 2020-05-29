#import interface

def interp(AST, env):
    AST_type = AST["type"]

    if AST_type == "Struct":
        interp_struct(AST, env)
    elif AST_type == "Action":
        interp_action(AST, env)
    else:
        raise SyntaxError("Invalid AST type in interp: " + AST_type)

def interp_struct(AST, env):
    stype = AST["stype"]

    if stype == "Main":
        for element in AST["seq"]:
            interp(element, env)
    elif stype == "Iter":
        items = AST["items"]
        var = AST["var"]

        already_exists = False

        if var in env:
            already_exists = True
            temp = env[var]

        env.update({var: None})

        for item in items:
            env[var] = item
            
            for element in AST["iter"]:
                interp(element, env)

        if already_exists == True:
            env[var] = temp

    else:
        raise SyntaxError("Invalid struct type in interp_struct: " + stype)

def interp_action(action, env):
    atype = action["atype"]

    if atype == "Print":
        print(interp_atom(action["args"], env))
    elif atype == "Set":
        env[action["args"][0]] = interp_atom(action["args"][1], env)
    elif atype == "Add" or atype == "Sub" or atype == "Mul" or atype == "Div":
        env[action["args"][0]] = bin_op(interp_atom(action["args"][1], env), interp_atom(action["args"][2], env), atype)
    else: 
        raise SyntaxError("Invalid action type in interp_action: " + atype)

def interp_atom(atom, env):
    if atom == "" or atom is None:
        raise SyntaxError("Missing arg or empty arg in interp_atom")
    
    DISCORD_INTERFACE = False

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
