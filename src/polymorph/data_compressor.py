import zlib, base64, ast, pickle

'''
Comrade - object compressor
Written for compressing message cache list
'''

def compressObj(d, level):
    '''
    turns {dictionary, list} object into compressed text.
    '''
    text = str(d)
    code =  base64.b64encode(
        zlib.compress(
            text.encode("utf-8"), level)
        ).decode("utf-8")
    return code

def decompressObj(code):
    '''
    Decompresses an object
    '''
    data = zlib.decompress(base64.b64decode(code)).decode("utf-8")
    d = ast.literal_eval(data)
    return d


