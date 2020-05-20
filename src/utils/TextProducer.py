import pickle
from utils.textgenut import *
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

    if num_tokens < len(seed):
        for i in range(0, num_tokens):
            result.append(seed[i])
    else:
        result[0:len(seed)] = seed # populate with first N tokens

        n_len = 0 # length of each n-gram must be determined
        for k in ngram_model.keys():
            n_len = len(k) # length of key will be length of gram
        
        # use last n_len words of seed to generate next
        n_pos = 0 # position pointer for where to generate next n-gram (should always by zero given spec doc)
        # THIS IS MADE UNDER THE STRICT ASSUMPTION THAT SEED LENGTH WILL ALWAYS BE EQUAL TO N-GRAM LENGTH

        current_n = ['']*n_len
        for i in range(n_len):
            current_n[i] = result[i+n_pos]
        current_n = tuple(current_n)

        while len(result) < num_tokens and current_n in ngram_model.keys() and check_open_ngram(current_n, ngram_model):
        # take advantage of lazy evaluation to check conditions in sequence
        # validate all conditions to proceed
            result.append(gen_next_token(current_n, ngram_model))
            n_pos += 1 # advance pointer to next position to start generating next n-gram

            current_n = ['']*n_len
            for i in range(n_len):
                current_n[i] = result[i+n_pos]
            current_n = tuple(current_n)
            
    return result

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

def text(modelname, maxlength):
    with open(modelname, "rb") as f:
        model = pickle.load(f)
    return gen_bot_text(gen_bot_list(model, gen_seed(model), maxlength))

if __name__ == "__main__":
    for i in range(20):
        print(text("Prose Model.mdl", 10) + "\n")