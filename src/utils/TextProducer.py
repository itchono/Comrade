import pickle
from textgenut import *
import re

model = {}

def gen_bot_list(ngram_model, seed, num_tokens=0):
    '''
    (dict<n-gram>, tuple<str>, int) -> list<str>

    gen_bot_list returns a randomly generated list of tokens beginning with the first three tokens of seed,
    and selecting all subsequent tokens using gen_next_token (utilities.py). 

    it is assumed that the seed size and gram size are the same.

    list is terminated once length reaches num_tokens, or if current ngram is not in the model, or the current ngram has no proceeding outputs.

    See spec doc for examples.
    '''
    result = []
    # initialize empty list

    if num_tokens >= len(seed):
        result[0:len(seed)] = seed # populate with first N tokens

        n_len = len(seed) #n-gram length

        n_pos = 0

        current_n = tuple([result[i+n_pos] for i in range(n_len)]) 

        cont = True

        while len(result) < num_tokens and cont:
            try:
                cont = check_open_ngram(current_n, ngram_model)
                result.append(gen_next_token(current_n, ngram_model))
                n_pos += 1 # advance pointer to next position to start generating next n-gram

                current_n = tuple([result[i+n_pos] for i in range(n_len)]) 
            except:
                cont = False
        
        return result
    
    else:
        return seed[0:num_tokens]
        

def gen_bot_text(token_list):
    '''
    (list<str>, bool) -> str

    gen_bot_text takes in a list of tokens and returns a string depending on the bool input
    if true: returns the list concatenated into a strin
    if false: processes it with grammar rules as per spec doc.

    See spec doc for examples.
    '''
    s = ' '.join(token_list)

    s = s.translate(str.maketrans("", "", "\n"))

    return s

def text(model, maxlength):
    return gen_bot_text(gen_bot_list(model, gen_seed(model), maxlength))

if __name__ == "__main__":
    with open("Prose Model.mdl", "rb") as f:
        modelKZ = pickle.load(f)
        for i in range(20):
            print(text(modelKZ, 10) + "\n")