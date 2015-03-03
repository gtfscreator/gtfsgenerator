def stem(word):
    """ Stem word to primitive form """
    return word.lower().rstrip(",.!:;'-\"").lstrip("'\"")

word='Francesco , Mario,!!!:'

print word.split()
