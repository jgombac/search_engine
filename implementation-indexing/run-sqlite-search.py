import nltk

import database as db
import preprocessing as pp


relative_path = "../pages/"


def create_snippets(result, count):
    file = pp.get_file(f"{relative_path}{result.document_name}", 'utf8')
    text = pp.get_text(file)
    tokens = nltk.word_tokenize(text)
    index = result.indexes[0][0]
    return tokens[int(index)-20:int(index)+20]



if __name__ == '__main__':
    con = db.connection()

    query = "varnost in zdravje"
    query_tokens = pp.preprocess_query(query)
    print(query_tokens)

    results = db.get_all_multiword_postings_alt(con, query_tokens)
    print(len(results))
    print(results)
    print(create_snippets(results[0], 1))
    print("done")
