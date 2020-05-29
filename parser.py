import re

def token_list(input_str):
    return input_str.splitlines()

def token_line(input_str):
    return input_str.split()

def get_env(splt_line_lst):
    first_line = splt_line_lst.pop(0)

    if re.search(r"\[((([a-zA-Z])+\,)+(([a-zA-Z])+)|([a-zA-Z]+))\]", first_line) is None:
        raise SyntaxError("Missing or incorrect function parameters")

    env_list = first_line.replace("[", "").replace("]", "").replace(",", " ").split()

    env_dict = {}

    for var in env_list:
        env_dict[var] = None

    return env_dict


def parse(program):
    seq = {"type": "Struct", "stype": "Main", "seq": []}

    while len(program) > 0:
        seq["seq"].append(parse_struct(program))

    return seq;

def parse_struct(program):
    line = program.pop(0).split()

    if line[0] == "ITER":
        loop = {"type": "Struct", "stype": "Iter", "iter": [], "var": line[1], "items": line[2].replace("[", "").replace("]", "").split(",")}

        while program[0].split()[0] != "ITEREND":
            loop["iter"].append(parse_struct(program))
        program.pop(0)
        return loop
    elif line[0] == "WHILE":
        loop = {"type": "Struct", "stype": "While", "while": [], "cond": line[1:]}

        while program[0].split()[0] != "WHILEEND":
            loop["while"].append(parse_struct(program))
        program.pop(0)
        return loop
    else:
        return parse_action(line[0], line[1:])

def parse_action(cmd, line):
    if cmd == "CALL":
        return {"type": "Action", "atype": "Call", "args": line}
    elif cmd == "PRINT":
        return {"type": "Action", "atype": "Print", "args": line.pop(0)}
    elif cmd == "SET":
        return {"type": "Action", "atype": "Set", "args": line}
    elif cmd == "ADD":
        return {"type": "Action", "atype": "Add", "args": line}
    elif cmd == "SUB":
        return {"type": "Action", "atype": "Sub", "args": line}
    elif cmd == "MUL":
        return {"type": "Action", "atype": "Mul", "args": line}
    elif cmd == "DIV":
        return {"type": "Action", "atype": "Div", "args": line}
    else:
        errorStr = "Unknown action: " + cmd + " with args: " + "".join(line)
        raise SyntaxError(errorStr)

if __name__ == "__main__":
    #take in input as string
    input_str = "[style, them]\nSET test 4\nPRINT &test\nWHILE test > 1\nCALL $c avatar itchono\nITER beta [cool,when]\nPRINT heyo\nITEREND hehe\nSUB test &test 1\nWHILEEND\nPRINT hi"

    #seperate program into individual lines
    splt_line_lst = token_list(input_str)

    #get env from first line
    env = get_env(splt_line_lst)
    
    #parse program
    ast = parse(splt_line_lst)

    print("ast:", ast)
