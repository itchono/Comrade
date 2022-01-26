import random
from dis_snek.models.discord import CustomEmoji


def owoify(t: str):
    '''
    Replaces L, R, with W (match case)
    '''
    remove_characters = ["R", "L", "r", "l"]
    for character in remove_characters:
        if character.islower():
            t = t.replace(character, "w")
        else:
            t = t.replace(character, "W")
    return t


def emojify(emojis: list[CustomEmoji], t: str):
    '''
    Substitute spaces with emojis from a guild
    '''
    return "".join([str(random.choice(emojis))
                    if s == " " else s for s in t])


def mock(t: str):
    '''
    Randomly captializes and lowercases letters in string
    '''
    return "".join([random.choice([c.upper(), c.lower()]) for c in t])
