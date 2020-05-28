import zlib, base64, json, pickle

'''
Comrade - object compressor
Written for compressing message cache list
'''

def compressCache(cache, level):
    '''
    turns tuple-less dictionary [JSON] into text
    '''
    d = {"cache":cache}

    text = json.dumps(d)
    
    code =  base64.b64encode(
        zlib.compress(
            text.encode("utf-8"), level)
        ).decode("utf-8")
    return code

def decompressCache(code):
    '''
    Decompresses a json
    '''
    data = zlib.decompress(base64.b64decode(code)).decode("utf-8")
    d = json.loads(data)
    return d["cache"]


