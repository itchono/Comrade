import random

VALID_PUNCTUATION = ['?', '.' , '!', ',', ':', ';']
END_OF_SENTENCE_PUNCTUATION = ['?', '.', '!']
ALWAYS_CAPITALIZE = ["I", "Montmorency", "George", "Harris", "J", "London", "Thames", "Liverpool", \
                     "Flatland", "", "Mrs", "Ms", "Mr", "William", "Samuel"]
BAD_CHARS = ['"', "(", ")", "{", "}", "[", "]", "_"]
    
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
    keys of the ngram_model. You are guaranteed that the generated
    seed (i.e. tuple) will contain no punctuation.

    The function assumes that there is at least one tuple without punctuation that
    has a non-empty list of words associated with it.
    '''
    ngram_model_key_list = sorted(list(ngram_model)) # sort for repeatability
    ngram = random.choice(ngram_model_key_list)

    
    punc_in_ngram = False
    for item in ngram:
        if item in VALID_PUNCTUATION:
            punc_in_ngram = True
    
    while not check_open_ngram(ngram, ngram_model) or punc_in_ngram:
        ngram = random.choice(ngram_model_key_list)

        punc_in_ngram = False
        for item in ngram:
            if item in VALID_PUNCTUATION:
                punc_in_ngram = True
    
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
    cdf = ngram_model[current_ngram][1].copy()
    
    for i in range(1, len(cdf)):
        cdf[i] += cdf[i-1]

    while cdf[prob_to_index] < curr_prob:
        prob_to_index += 1

    return words[prob_to_index]
