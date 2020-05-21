import time
from functools import reduce
from sys import argv

import preprocessing as pp
import tqdm
from database import Posting
from utils import get_page_filenames, get_file


relative_path = "../pages/"


class Snippet:
    def __init__(self, text, front, back):
        self.text = text
        self.front = front
        self.back = back

    def __repr__(self):
        return self.text


class Result:
    def __init__(self, document_name, frequency_sum, indexes):
        self.document_name = document_name
        self.frequency_sum = frequency_sum
        self.indexes = indexes


def create_snippets(result, width):
    file = pp.get_file(f"{relative_path}{result.document_name}", 'utf8')
    text = pp.get_text(file)

    snippets = list()
    indexes = list()

    word_count = 0

    for c in range(len(result.indexes)):
        index = result.indexes[c][0]
        if index in indexes:
            continue
        indexes.append(index)

        snippet = text[index]
        front = True
        back = True
        try:
            for i in range(index + 1, len(text)):
                if i <= len(text) - 2:
                    stop = text[i:i + 2]
                    if stop == '. ':
                        snippet += '.'
                        back = False
                        break
                char = text[i]
                if char == ' ':
                    word_count += 1
                    if word_count > width:
                        word_count = 0
                        break
                indexes.append(i)
                snippet += char
        except IndexError:
            pass
        try:
            for i in range(index - 1, -1, -1):
                if i >= 2:
                    stop = text[i - 1:i + 1]
                    if stop == '. ':
                        front = False
                        break
                char = text[i]
                if char == ' ':
                    word_count += 1
                    if word_count > width:
                        word_count = 0
                        break
                indexes.append(i)
                snippet = char + snippet
        except IndexError:
            pass
        snippets.append(Snippet(snippet.replace('\n', ''), front, back))
    return snippets


def get_all_multiword_postings(query_tokens):
    results = []

    filenames = get_page_filenames()
    for filename in tqdm.tqdm(filenames):
        file = get_file(filename, "utf8")
        text = pp.get_text(file)
        words = pp.preprocess(text)

        postings = []
        frequency_sum = 0

        for token in query_tokens:
            posting = Posting(token, filename, 0, [])
            for word in words:
                if word[0] == token:
                    posting.frequency += 1
                    posting.indexes.append(word[1])

            if posting.frequency > 0:
                postings.append(posting)
                frequency_sum += posting.frequency

        if len(query_tokens) == len(postings):
            document_name = filename[9:].replace("\\", "/")
            indexes = []
            for p in postings:
                indexes.append(sorted(p.indexes))

            result = Result(document_name, frequency_sum, indexes)
            results.append(result)

    return sorted(results, key=lambda r: r.frequency_sum, reverse=True)


def find(query, result_count):
    start_time = time.perf_counter_ns()
    query_tokens = pp.preprocess_query(query)
    results = get_all_multiword_postings(query_tokens)
    end_time = time.perf_counter_ns()
    search_time = round((end_time - start_time) / 1000000)

    result_count = min(len(results), result_count)
    tab = ' ' * 2
    freq = 'Frequencies'
    doc = 'Document'
    snip = 'Snippet'
    longest_name = 0
    for i in range(result_count):
        if len(results[i].document_name) > longest_name:
            longest_name = len(results[i].document_name)
    longest_name = max(longest_name, len(doc))

    print(f"Results for query: \"{query}\"")
    print()
    print(f"{tab}Results found in {search_time}ms.")
    print(f"{tab}{freq} {doc}{' ' * (longest_name - len(doc))} {snip}")
    print()
    print(f"{tab}{'-' * len(freq)} {'-' * longest_name} {'-' * longest_name}")
    for i in range(result_count):
        result = results[i]
        snippets = create_snippets(result, 3)
        snippet_string = ''
        for j in range(len(snippets)):
            snippet = snippets[j]
            if snippet.front:
                if j == 0:
                    snippet_string += '... '
                elif not snippets[j - 1].back:
                    snippet_string += '... '
            snippet_string += snippet.text
            if snippet.back:
                snippet_string += ' ... '
            else:
                snippet_string += ' '
        print(f"{tab}{result.frequency_sum}{' ' * (len(freq) - len(str(result.frequency_sum)))} {result.document_name}"
              f"{' ' * (longest_name - len(result.document_name))} {snippet_string}")
    print()


if __name__ == '__main__':
    if len(argv) > 1:
        find(argv[1], 5)
    else:
        queries = [
            "predelovalne dejavnosti",
            "trgovina",
            "social services",

            "sistem SPOT",
            "EVEM",
            "Registracija samostojnega podjetnika"
        ]
        for query in queries:
            find(query, 5)
