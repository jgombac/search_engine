import nltk
import time
import database as db
import preprocessing as pp


relative_path = "../pages/"


class Snippet:

    def __init__(self, text, front, back):
        self.text = text
        self.front = front
        self.back = back

    def __repr__(self):
        return self.text


def create_snippets(result, width):
    file = pp.get_file(f"{relative_path}{result.document_name}", 'utf8')
    text = pp.get_text(file)
    tokens = nltk.word_tokenize(text)

    snippets = list()
    indexes = list()

    for w in range(len(result.indexes)):
        index = int(result.indexes[w][0])
        if index in indexes:
            continue
        indexes.append(index)

        snippet = tokens[index]
        front = True
        back = True
        try:
            for i in range(1, width):
                word = tokens[index + i]
                if word == '.':
                    snippet += '.'
                    back = False
                    break
                indexes.append(index + i)
                snippet += f" {word}"
        except IndexError:
            pass
        try:
            for i in range(1, width):
                word = tokens[index - i]
                if word == '.':
                    front = False
                    break
                indexes.append(index - i)
                snippet = f"{word} {snippet}"
        except IndexError:
            pass
        snippets.append(Snippet(snippet, front, back))
    return snippets


if __name__ == '__main__':
    con = db.connection()
    tab = ' '*2
    freq = 'Frequencies'
    doc = 'Document'
    snip = 'Snippet'

    result_count = 5
    query = "predelovalne dejavnosti"

    start_time = time.perf_counter_ns()
    query_tokens = pp.preprocess_query(query)
    results = db.get_all_multiword_postings_alt(con, query_tokens)
    end_time = time.perf_counter_ns()
    search_time = round((end_time - start_time) / 1000000)

    result_count = min(len(results), result_count)

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
                elif not snippets[j-1].back:
                    snippet_string += '... '
            snippet_string += snippet.text
            if snippet.back:
                snippet_string += ' ... '
            else:
                snippet_string += ' '
        print(f"{tab}{result.frequency_sum}{' ' * (len(freq) - len(str(result.frequency_sum)))} {result.document_name}"
              f"{' ' * (longest_name - len(result.document_name))} {snippet_string}")