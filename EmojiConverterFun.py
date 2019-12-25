def textToEmoji(s):
    '''
    Converts text to equivalent emoji
    '''
    lookupTable = {"a":u"\U0001F1E6","b":u"\U0001F1E7","c":u"\U0001F1E8","d":u"\U0001F1E9","e":u"\U0001F1EA","f":u"\U0001F1EB","g":u"\U0001F1EC","h":u"\U0001F1ED","i":u"\U0001F1EE","j":u"\U0001F1EF","k":u"\U0001F1F0","l":u"\U0001F1F1","m":u"\U0001F1F2","n":u"\U0001F1F3","o":u"\U0001F1F4","p":u"\U0001F1F5","q":u"\U0001F1F6","r":u"\U0001F1F7","s":u"\U0001F1F8","t":u"\U0001F1F9","u":u"\U0001F1FA","v":u"\U0001F1FB","w":u"\U0001F1FC","x":u"\U0001F1FD","y":u"\U0001F1FE","z":u"\U0001F1FF"}

    s = s.lower()

    newS = ''
    for c in s:
        if c in lookupTable:
            newS += lookupTable[c] + " "
        else:
            newS += c
    return newS

if __name__ == "__main__":
    '''
    Quick demo of emoji converter in a pinch
    '''

    s = input("Input string:\n")
    print(textToEmoji(s))
