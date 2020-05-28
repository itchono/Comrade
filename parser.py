import re
#import comrade_interface from interface

def token_list(input_str):
    return input_str.splitlines()

def token_line(input_str):
    return input_str.split()

def get_env(splt_line_lst):
    first_line = splt_line_lst.pop(0)

    if re.search(r"\[((([a-zA-Z])+\,\s)+(([a-zA-Z])+)|([a-zA-Z]+))\]", first_line) is None:
        raise SyntaxError("Missing or incorrect function parameters")

    env_list = first_line.replace("[", "").replace("]", "").replace(",", "").split()

    env_dict = {}

    for var in env_list:
        env_dict[var] = None

    return env_dict

def parse_program(program):
    ast = {"type": "Sequence", "seq": []}

    for i in range(len(program)):
        line = program.pop(0)
        parse_line(line, program, ast["seq"])

    return ast

def parse_line(line, program, seq):
    splt_line = token_line(line)
    
    cmd = splt_line.pop(0)

    if cmd == "LOOP":
        print("looping???")
        raise SyntaxError("loop?")
    else:
        seq.append({"type": "Action", "action": parse_action(cmd, splt_line)})

def parse_action(cmd, line):
    if cmd == "CALL":
        return {"type": "Call", "args": line}
    elif cmd == "PRINT":
        return {"type": "Print", "args": line.pop(0)}
    elif cmd == "SET":
        return {"type": "Set", "args": line}
    elif cmd == "ADD":
        return {"type": "Add", "args": line}
    elif cmd == "SUB":
        return {"type": "Add", "args": line}
    elif cmd == "MUL":
        return {"type": "Add", "args": line}
    elif cmd == "DIV":
        return {"type": "Add", "args": line}
    else:
        errorStr = "Unknown action: " + cmd + " with args: " + "".join(line)
        raise SyntaxError(errorStr)

if __name__ == "__main__":
    #take in input as string
    input_str = "[stylem, things]\nPRINT 3\nPRINT 4\nCALL $c avatar itchono"

    #seperate program into individual lines
    splt_line_lst = token_list(input_str)

    #get env from first line
    env = get_env(splt_line_lst)
    
    #parse program
    ast = parse_program(splt_line_lst)

    print("ast:", ast)
