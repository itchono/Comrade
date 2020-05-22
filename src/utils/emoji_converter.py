'''
Comrade - Emoji Converter
Turns text into emoji and vice versa
'''

def emojiToText(s):
    '''
    Converts emoji to closest real text representation (lowercase output)
    Note: Will strip spaces.
    '''
    lookupTable = {u"\U0001F1E6":"a",u"\U0001F1E7":"b",u"\U0001F1E8":"c",u"\U0001F1E9":"d",u"\U0001F1EA":"e",u"\U0001F1EB":"f",u"\U0001F1EC":"g",u"\U0001F1ED":"h",u"\U0001F1EE":"i",u"\U0001F1EF":"j",u"\U0001F1F0":"k",u"\U0001F1F1":"l",u"\U0001F1F2":"m",u"\U0001F1F3":"n",u"\U0001F1F4":"o",u"\U0001F1F5":"p",u"\U0001F1F6":"q",u"\U0001F1F7":"r",u"\U0001F1F8":"s",u"\U0001F1F9":"t",u"\U0001F1FA":"u",u"\U0001F1FB":"v",u"\U0001F1FC":"w",u"\U0001F1FD":"x",u"\U0001F1FE":"y",u"\U0001F1FF":"z", 
    "0️⃣":0,"1️⃣":1,"2️⃣":2,"3️⃣":3,"4️⃣":4,"5️⃣":5,"6️⃣":6,"7️⃣":7,"8️⃣":8,"9️⃣":9}

    newS = ''

    i = 0

    while i < len(s):
        if s[i] in lookupTable:
            newS += lookupTable[s[i]]
            i += 1
        else:
            newS += s[i]
        i += 1
    return newS

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
        elif c in "0123456789":
            newS += {0:":zero:", 1:":one:", 2:":two:", 3:":three:", 4:":four:", 5:":five:", 6:":six:", 7:":seven:", 8:":eight:", 9:":nine:"}[int(c)]
        else:
            newS += c
    return newS


if __name__ == "__main__":
    print(textToEmoji(input("Text?")))