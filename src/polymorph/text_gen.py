import pickle
import re
import time
import random
    
def check_open_ngram(current_ngram, ngram_model):
    '''
    (tup, Dict{tup: List[List[int]]}) -> Bool
    
    Checks the current value associated with the n-gram key
    in ngram_model. Returns True for non-empty list,
    False for an empty list of tokens that follow it.

    check_open_ngram assumes that current_ngram exists as a
    key in ngram_model.
    '''
    return not ngram_model[current_ngram][0] == []

def gen_seed(ngram_model):
    '''
    (Dict{tup: List[List[int]]}) -> tup
    
    Returns a tuple of length n by selecting a random n-gram from the
    keys of the ngram_model.
    '''
    ngram_model_key_list = list(ngram_model)
    ngram = random.choice(ngram_model_key_list)
    
    while not check_open_ngram(ngram, ngram_model):
        ngram = random.choice(ngram_model_key_list)
    return ngram

def gen_next_token(current_ngram, ngram_model):
    '''
    (tup, Dict{tup: List[List[int]]}) -> str

    Randomly generates the next token from the current_ngram based on the 
    frequency of each word stored in ngram_model by sampling from the
    distribution of possible next words.
    
    The function assumes that check_open_ngram(ngram_model, current_ngram) is True, 
    i.e. that the array of words corresponding to ngram_model[current_ngram] 
    is not empty. The function also assumes that current_ngram is in ngram_model.
    '''
    curr_prob = random.random()
    prob_to_index = 0

    words = ngram_model[current_ngram][0]
    # create a copy that the code below does not modify the ngram model
    # Note: shallow copy is sufficient for a list of numbers
    cdf = ngram_model[current_ngram][1][:]
    
    for i in range(1, len(cdf)):
        cdf[i] += cdf[i-1]

    while cdf[prob_to_index] < curr_prob:
        prob_to_index += 1

    return words[prob_to_index]


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
        n_len = len(seed) #n-gram length

        result[0:len(seed)] = seed # populate with first N tokens

        current_n = tuple(result[-n_len:])

        cont = True

        while len(result) < num_tokens and cont:
            try:
                cont = check_open_ngram(current_n, ngram_model)
                result.append(gen_next_token(current_n, ngram_model))
                current_n = tuple(result[-n_len:])
            except: cont = False
        
        return result
    
    else: return seed[0:num_tokens]
        

def gen_bot_text(token_list):
    '''
    turns list into printable string
    '''
    s = ' '.join(token_list)
    s2 = ""

    for i in range(len(s)):
        if not (s[i] == " " and s[i-1] == "\n"): s2 += s[i]
    return s2

def text(model, maxlength):
    '''
    Generates a single instance of text up to some maximum length
    '''
    return gen_bot_text(gen_bot_list(model, gen_seed(model), maxlength))

if __name__ == "__main__":

    fname = input("Filename? (.mdl)")

    with open("{}.mdl".format(fname), "rb") as f:
        model = pickle.load(f)
        for i in range(5):
            t_start = time.perf_counter()
            print(text(model, 20) + "\n")
            print("Time: {}".format(time.perf_counter()-t_start))