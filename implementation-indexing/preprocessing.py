import nltk
from slovene_stemmer import stem
import stopwords
from utils import *
from bs4 import BeautifulSoup


def get_text(html):
    soup = BeautifulSoup(html, features="lxml")
    for removable in soup(["script", "style"]):
        removable.extract()
    meta = " ".join(
        [x.get("content") for x in soup.findAll("meta")
         if x.get("name") in ["title", "keywords", "description"] and x.get("content")])

    text = meta + " " + soup.get_text(" ", strip=True)

    return text


def preprocess(text):
    text = text.lower()
    tokens = get_tokens(text)
    removed = remove_stopwords(tokens)
    return removed


def get_tokens(text):
    return [(token, i) for i, token in enumerate(nltk.word_tokenize(text))]


def get_stemmed(tokens):
    return [(stem(x[0])[0], x[1]) for x in tokens]


def remove_stopwords(tokens):
    return [t for t in tokens if t[0].isalpha() and t[0] not in stopwords.stop_words_slovene]



# if __name__ == '__main__':
#     html = get_file("../pages/evem.gov.si/evem.gov.si.4.html", "utf8")
#     text = get_text(html)
#     preprocess(text)