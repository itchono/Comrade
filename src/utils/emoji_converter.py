'''
Comrade - Emoji Converter
Turns text into emoji and vice versa
'''
from string import ascii_lowercase

def emojiToText(s):
    '''
    Converts emoji to closest real text representation (lowercase output)
    Note: Will strip spaces.
    '''
    lookupTable = {u"\U0001F1E6":"a",u"\U0001F1E7":"b",u"\U0001F1E8":"c",u"\U0001F1E9":"d",u"\U0001F1EA":"e",u"\U0001F1EB":"f",u"\U0001F1EC":"g",u"\U0001F1ED":"h",u"\U0001F1EE":"i",u"\U0001F1EF":"j",u"\U0001F1F0":"k",u"\U0001F1F1":"l",u"\U0001F1F2":"m",u"\U0001F1F3":"n",u"\U0001F1F4":"o",u"\U0001F1F5":"p",u"\U0001F1F6":"q",u"\U0001F1F7":"r",u"\U0001F1F8":"s",u"\U0001F1F9":"t",u"\U0001F1FA":"u",u"\U0001F1FB":"v",u"\U0001F1FC":"w",u"\U0001F1FD":"x",u"\U0001F1FE":"y",u"\U0001F1FF":"z"}

    newS = ''
    for c in s:
        if c in lookupTable:
            newS += lookupTable[c]
        else:
            newS += c
    return newS

def textToEmoji(s):
    '''
    Converts text to equivalent emoji
    '''

    s = s.lower()

    newS = ''
    for c in s:
        if c in ascii_lowercase:
            newS += ":regional_indicator_{}:".format(c)
        elif c in "0123456789":
            newS += {0:":zero:", 1:":one:", 2:":two:", 3:":three:", 4:":four:", 5:":five:", 6:":six:", 7:":seven:", 8:":eight:", 9:":nine:"}[int(c)]
        else:
            newS += c
    return newS

def makelookuptable():
    pass


if __name__ == "__main__":
    print(textToEmoji("hello sir"))