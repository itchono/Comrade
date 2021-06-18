import re
import ast


def token_list(input_str):
    return input_str.splitlines()


def token_line(input_str):
    return input_str.split()


def get_env(splt_line_lst):
    first_line = splt_line_lst[0]

    if first_line[-1] != "]" and first_line[0] != "[":
        return {}  # empty params
    else:
        splt_line_lst.pop(0)
        env_list = first_line.replace("[", "").replace("]", "").split(",")
        return {var_pair.strip(" ").split("=")[0]: var_pair.strip(" ").split("=")[
            1] for var_pair in env_list}  # NOTE cosmo takes in string literals for everything


def parse(program):
    seq = {"type": "Struct", "stype": "Main", "seq": []}

    while len(program) > 0:
        seq["seq"].append(parse_struct(program))

    return seq


def parse_struct(program):
    line = program.pop(0).split()

    if line[0] == "ITER":
        loop = {
            "type": "Struct",
            "stype": "Iter",
            "iter": [],
            "var": line[1],
            "items": line[2].replace(
                "[",
                "").replace(
                "]",
                "").split(",")}

        while program[0].split()[0] != "ITEREND":
            loop["iter"].append(parse_struct(program))
        program.pop(0)
        return loop
    elif line[0] == "WHILE":
        loop = {"type": "Struct", "stype": "While",
                "while": [], "cond": line[1:]}

        while program[0].split()[0] != "WHILEEND":
            loop["while"].append(parse_struct(program))
        program.pop(0)
        return loop
    elif line[0] == "COND":
        cond = {"type": "Struct", "stype": "Cond", "case": []}

        while program[0].split()[0] != "CONDEND":
            cond["case"].append(parse_struct(program))
        program.pop(0)
        return cond
    elif line[0] == "CASE":
        case = {"type": "Struct", "stype": "Case",
                "case": [], "cond": line[1:]}

        cmd = program[0].split()[0]
        while cmd != "CASE" and cmd != "CONDEND":
            case["case"].append(parse_struct(program))
            cmd = program[0].split()[0]
        return case
    elif line[0] == "ELSE":
        case = {
            "type": "Struct",
            "stype": "Case",
            "case": [],
            "cond": ["true"]}

        cmd = program[0].split()[0]
        while cmd != "CASE" and cmd != "CONDEND":
            case["case"].append(parse_struct(program))
            cmd = program[0].split()[0]
        return case
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
