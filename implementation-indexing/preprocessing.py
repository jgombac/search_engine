import nltk
import stopwords

def preprocess(text):
    tokens = tokenize(text)
    normalized = normalize(tokens)
    removed = remove_stopwords(normalized)


def tokenize(text):
    pass


def remove_stopwords(tokens):
    pass


def normalize(tokens):
    pass