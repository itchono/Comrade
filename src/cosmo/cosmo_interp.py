from utils.utilities import *

# MODIFIED SYSTEM to interpret Cosmo code, in a way that works with Comrade.

INTERP_TIMEOUT = 1 # number of seconds allowed for parser to operate before terminating

CMD_STACK = []

def fill_env(env):
    for var in env:
        env[var] = input()

async def interp(AST, env, extCall = False):

    if extCall: CMD_STACK.clear() # putput system

    AST_type = AST["type"]

    if AST_type == "Struct":
        await asyncio.wait_for(interp_struct(AST, env), timeout=INTERP_TIMEOUT)
    elif AST_type == "Action":
        await asyncio.wait_for(interp_action(AST, env), timeout=INTERP_TIMEOUT)
    else:
        raise SyntaxError("Invalid AST type in interp: " + AST_type)

    if extCall: return CMD_STACK

async def interp_struct(AST, env):
    stype = AST["stype"]

    if stype == "Main":
        for element in AST["seq"]:
            await asyncio.wait_for(interp(element, env), timeout=INTERP_TIMEOUT)
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
                await asyncio.wait_for(interp(element, env), timeout=INTERP_TIMEOUT)

        if already_exists == True:
            env[var] = temp
    elif stype == "While":
        loop_bool = interp_bool(AST["cond"], env)

        while loop_bool:
            for element in AST["while"]:
                await asyncio.wait_for(interp(element, env), timeout=INTERP_TIMEOUT)

            loop_bool = interp_bool(AST["cond"], env)
    elif stype == "Cond":
        for case in AST["case"]:
            if interp_bool(case["cond"], env):
                for element in case["case"]:
                    await asyncio.wait_for(interp(element, env), timeout=INTERP_TIMEOUT)
                break
    else:
        raise SyntaxError("Invalid struct type in interp_struct: " + stype)

async def interp_action(action, env):
    atype = action["atype"]
    if atype == "Print":
        print(interp_atom(action["args"], env))
    elif atype == "Set":
        env[action["args"][0]] = interp_atom(action["args"][1], env)
    elif atype == "Add" or atype == "Sub" or atype == "Mul" or atype == "Div":
        env[action["args"][0]] = bin_op(interp_atom(action["args"][1], env), interp_atom(action["args"][2], env), atype)
    
    
    elif atype == "Call":
        await asyncio.wait_for(interp_call(action["args"], env), timeout=INTERP_TIMEOUT)
    else: 
        raise SyntaxError("Invalid action type in interp_action: " + atype)

def interp_atom(atom, env):
    if atom == "" or atom is None:
        raise SyntaxError("Missing arg or empty arg in interp_atom")

    # REQUIRED TO TREAT THE VARIABLE AS A VARIABLE INSTEAD OF A STRING LITERAL
    if atom[0] == "&" and atom[1:] in env:
        return env[atom[1:]]
    else:
        return atom
    """
    NOTE: This allows arbitrary code execution, don't do it
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

def interp_bool(bool_stmt, env):
    if len(bool_stmt) == 3:

        """try: a = ast.literal_eval(bool_stmt[0])
        except: 

        try: b = ast.literal_eval(bool_stmt[2])
        except: """
        
        a = bool_stmt[0]
        b = bool_stmt[2]
        c = bool_stmt[1]

        if c == "==":
            return interp_atom(a, env) == interp_atom(b, env)
        elif c == "!=":
            return interp_atom(a, env) != interp_atom(b, env)
        elif c == ">":
            return interp_atom(a, env) > interp_atom(b, env)
        elif c == "<":
            return interp_atom(a, env) < interp_atom(b, env)
        elif c == ">=":
            return interp_atom(a, env) >= interp_atom(b, env)
        elif c == "<=":
            return interp_atom(a, env) >= interp_atom(b, env)
        else:
            raise SyntaxError("not a valid boolean comparison in interp_bool: " + c)
    elif len(bool_stmt) == 1:
        bool_val = interp_atom(bool_stmt[0], env)

        if bool_val == "true":
            return True
        elif bool_val == "false":
            return False
        else:
            raise SyntaxError("Not a valid boolean value in interp_bool: " + bool_val)
    else:
        raise SyntaxError("Not a valid set of boolean arguments in interp_bool: " + str(bool_stmt))

async def interp_call(d_call, env):
    '''
    Adds to command stack
    '''
    out_str = ""
    for arg in d_call:
        out_str = out_str + interp_atom(arg, env) + " "
    CMD_STACK.append(out_str)
