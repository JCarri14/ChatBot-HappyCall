from nltk.tokenize import RegexpTokenizer

def sentence_to_tokens(term, sentence):
    tokenizer = RegexpTokenizer("[\w']+")
    words = tokenizer.tokenize(sentence)
    return words