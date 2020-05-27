import re
#import comrade_interface from interface

def token_list(input_str):
    return input_str.splitlines()

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
    


if __name__ == "__main__":
    #take in input as string
    input_str = "[stylem, things]\nhow are you\ndoing"

    #seperate program into individual lines
    splt_line_lst = token_list(input_str)
    print(splt_line_lst)

    #get env from first line
    env = get_env(splt_line_lst)
    print(env)
    print(splt_line_lst)
    
    ast = parse_program(splt_line_lst)
