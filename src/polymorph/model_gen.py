import re
import pickle
import json

def parse_arr(arr, reverse=False):
    '''
    cleans a long list of messages into list of usable words (lowercase letters only)
    '''
    arrclean = [(t.translate(str.maketrans("", "", "#!$%&:\"()*+,-./;<=>?@[\\]^_`{|}~")).lower()) for t in arr if (not (re.search(r"<*>|[0-9]{6,}|http", t) or t.encode("ascii", "ignore").decode() != t))]
    # remove complicating characters
    # arrclean is now a bunch of lines
    
    arrsuperclean = []
    for line in reversed(arrclean) if reverse else arrclean:
        arrsuperclean.extend(line.split(" "))
        '''
        arrsuperclean.extend(line.strip("\n").split(" "))
        arrsuperclean += ["\n"]
        '''

        # experimental stop token changes?

    return arrsuperclean

def build_ngram_model(words, n):
    '''
    Builds n-grams given a list of words extracted from the corpus.
    '''
    result = {}

    for i in range(0, len(words) - n):
        ng_tuple = tuple(words[i:i+n])
        word = words[i+n]

        try: result[ng_tuple][1][result[ng_tuple][0].index(word)] += 1 # if this is already in the model
        except:
            # if we cannot locate the word
            try:
                result[ng_tuple][0].append(word)
                result[ng_tuple][1].append(1)
            except: result[ng_tuple] = [[word],[1]] # if the gram is not even in the dictionary yet
    
    return {key:[value[0], [count/sum(value[1]) for count in value[1]]] for (key,value) in result.items()}
    # normalize probabilities to 1


def modelfrommsgs(msgs, n=3, reverse=True):
    t = parse_arr(msgs, reverse=reverse)
    m = build_ngram_model(t, n)
    return m

if __name__ == "__main__":
    fname = input("Filename? (.txt)")

    with open("{}.txt".format(fname), "r", encoding="utf-8") as f:
        t = parse_arr(f.read().split("\n"), reverse=True)

        mdl = build_ngram_model(t, 3)

        with open("{}.mdl".format(fname), "wb") as m:
          pickle.dump(mdl, m)

        print("Model built.")