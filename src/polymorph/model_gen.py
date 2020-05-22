import re
import pickle
import json

def parse_text(text, reverse=False):
    '''
    cleans a long string into list of usable words (lowercase letters only)
    outputs remainder.
    '''
    arr = text.split("\n")

    arrclean = []

    with open("remainder.txt", "w", encoding="utf-8") as f:
        for t in arr:

            if re.search("\$[a-zA-z]|<*>|[0-9]{6,}|http", t) or t.encode("ascii", "ignore").decode() != t:
                f.write(str(t+"\n"))
            else:
                arrclean.append(t.translate(str.maketrans("", "", "#!$%&:\"\'()*+,-./;<=>?@[\\]^_`{|}~")).lower())

    # arrclean is now a bunch of lines

    arrsuperclean = []

    with open("clean.txt", "w") as f:
      for line in reversed(arrclean) if reverse else arrclean:
          f.write(line + "\n")
          arrsuperclean.extend(line.split(" "))

    return arrsuperclean

def parse_arr(arr, reverse=False):
    '''
    cleans a long list of messages into list of usable words (lowercase letters only)
    '''

    arrclean = []
    for t in arr:
        if not (re.search("\$[a-zA-z]|<*>|[0-9]{6,}|http", t) or t.encode("ascii", "ignore").decode() != t):
           arrclean.append(t.translate(str.maketrans("", "", "#!$%&:\"\'()*+,-./;<=>?@[\\]^_`{|}~")).lower())

    # arrclean is now a bunch of lines
    arrsuperclean = []
    for line in reversed(arrclean) if reverse else arrclean:
        arrsuperclean.extend(line.split(" "))

    return arrsuperclean

def get_prob_from_count(counts):
    '''
    (list<number>) -> list<float>

    get_prob_from_count returns a list of probabilities derived from counts, where counts is a list of counts of occurrences of
    a token after the previous n-gram.

    >>> get_prob_from_count([10, 20, 40, 30])
    [0.1, 0.2, 0.4, 0.3]
    '''

    tot = sum(counts) # sum up number
    probs = [0] * len(counts)

    for i in range(0, len(counts)):
        probs[i] = counts[i]/tot
    return probs

def build_ngram_counts(words, n):
    '''
    (list<str>, int) -> dict

    build_ngram_counts returns a dictionary of n-grams and the counts of the words that follow the n-gram.
    The key will be the tuple containing words in a sequence.
    '''

    result = {} # empty dict

    # generate n-grams

    for i in range(0, len(words) - n):
        # main loop. used to define starting positions for each n-gram
        # no tokens proceed the 2nd-last n-gram, thus it does not need to be len(words) - n + 1.

        ng_tuple = tuple(words[i:i+n])
        word = words[i+n]

        try:
            # if this is already in the model
            result[ng_tuple][1][result[ng_tuple][0].index(word)] += 1
        except:
            # if we cannot locate the word
            try:
                result[ng_tuple][0].append(word)
                result[ng_tuple][1].append(1)
            except:
                # if the gram is not even in the dictionary yet
                result[ng_tuple] = [[word],[1]]

    return result

def prune_ngram_counts(counts, prune_len):
    '''
    (dict, int) -> dict

    prune_ngram_counts takes in a n-grams-with-counts dict with the same format as build_ngram_counts, 
    and removes entries in counts with low frequency. it will keep the prune_len highest frequency words. 
    If there is a tie, it will keep all tied words.
    '''
    result = {} # new empty dict for output

    for k in counts.keys():
        # init new array of survivors that will replace current counts
        
        # get list of frequencies from max to min using reverse sort
        freqs = sorted(counts[k][1], reverse=True)

        n = len(counts[k][1]) if (len(counts[k][1]) < prune_len) else prune_len
        # adjust prune length to fit array

        result[k] = [[counts[k][0][i] for i in range(0, len(counts[k][1])) if counts[k][1][i] >= freqs[n-1]], 
                    [counts[k][1][i] for i in range(0, len(counts[k][1])) if counts[k][1][i] >= freqs[n-1]]]
        # add only surviving elements to the dictionary

    return result 

def probify_ngram_counts(counts):
    '''
    (dict) -> dict

    probify_ngram_counts takes in a dict with the same output format as prune_ngram_counts, and converts the counts
    into probabilities.
    '''
    result = {} # new empty dict for output

    for k in counts.keys():
        result[k] = [counts[k][0], get_prob_from_count(counts[k][1])]
        # use preexisting function to convert to probabilities
    return result

def build_ngram_model(words, n):
    '''
    (list<str>, int) -> dict

    build_ngram_model returns a dict representing an n-gram-count model, given a size of n-gram (n) and an input set of words (words).
    This will take the 10 most common words, and show each count as a probability.
    '''
    return probify_ngram_counts(prune_ngram_counts(build_ngram_counts(words, n), 10)) # combine functions


def modelfrommsgs(msgs, n=3, reverse=True):
    t = parse_arr(msgs, reverse=reverse)
    m = build_ngram_model(t, n)
    '''with open("polymorph/{}.mdl".format(msgs[0].translate(str.maketrans("", "", "#!$%&:\"\'()*+,-./;<=>?@[\\]^_`{|}~"))), "wb") as f:
          pickle.dump(m, f)'''
    return m

if __name__ == "__main__":
    fname = input("Filename? (.txt)")

    with open("{}.txt".format(fname), "r", encoding="utf-8") as f:
        t = parse_text(f.read(), reverse=True)

        mdl = build_ngram_model(t, 3)

        with open("{}.mdl".format(fname), "wb") as m:
          pickle.dump(mdl, m)

        print("Model built.")