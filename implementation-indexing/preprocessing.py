import nltk
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


def preprocess_query(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    removed = [t for t in tokens if t.isalpha() and t not in stopwords.stop_words_slovene]
    return removed


def get_tokens(text):
    tokens = nltk.word_tokenize(text)
    result = []
    offset = 0
    for token in tokens:
        offset = text.find(token, offset)
        result.append((token, offset))
        offset += len(token)
    return result


def get_stemmed(tokens):
    return [(stem(x[0])[0], x[1]) for x in tokens]


def remove_stopwords(tokens):
    return [t for t in tokens if t[0].isalpha() and t[0] not in stopwords.stop_words_slovene]



if __name__ == '__main__':
    html = get_file("../pages/evem.gov.si/evem.gov.si.4.html", "utf8")
    text = get_text(html)
    text = text.lower()
    print(text[:200])
    tokens = get_tokens(text)
    print(tokens[:100])
    removed = remove_stopwords(tokens)
    print(removed)