import sqlite3

DB = "inverted-index.db"


def connection():
    return sqlite3.connect(DB)


def init_database():
    con = sqlite3.connect(DB)

    cur = con.cursor()
    cur.execute('''
                CREATE TABLE IndexWord (
                  word TEXT PRIMARY KEY
                );
            ''')
    cur.execute('''
                CREATE TABLE Posting (
                  word TEXT NOT NULL,
                  documentName TEXT NOT NULL,
                  frequency INTEGER NOT NULL,
                  indexes TEXT NOT NULL,
                  PRIMARY KEY(word, documentName),
                  FOREIGN KEY (word) REFERENCES IndexWord(word)
                );
            ''')
    con.commit()
    con.close()


class Posting:
    def __init__(self, word, document_name, frequency, indexes):
        self.word = word
        self.documentName = document_name
        self.frequency = int(frequency)
        self.indexes = parse_indexes(indexes) if isinstance(indexes, str) else indexes


class SearchResult:
    def __init__(self, document_name, frequency_sum, indexes):
        self.document_name = document_name
        self.frequency_sum = frequency_sum
        split = indexes.split(';')
        self.indexes = [el.split(',') for el in split]

    def __repr__(self):
        return f"[{self.document_name}, {self.frequency_sum}, {self.indexes}]"


def insert_index_word(con, index_word):
    cur = con.cursor()
    cur.execute("SELECT COUNT(1) FROM IndexWord WHERE word = ?", (index_word,))
    if not cur.fetchone()[0] > 0:
        cur.execute("INSERT INTO IndexWord VALUES (?)", (index_word,))
        con.commit()


def insert_posting(con, index_word, document_name):
    cur = con.cursor()
    cur.execute("INSERT INTO Posting VALUES (?, ?, ?, ?)", (index_word, document_name, 0, ""))
    con.commit()
    return Posting(index_word, document_name, 0, "")


def get_or_create_posting(con, index_word, document_name):
    cur = con.cursor()
    cur.execute("SELECT * FROM Posting WHERE word = ? AND documentName = ?", (index_word, document_name))
    res = cur.fetchone()
    if res:
        return Posting(res[0], res[1], res[2], res[3])
    return insert_posting(con, index_word, document_name)


def update_posting(con, index_word, document_name, index):
    cur = con.cursor()
    posting = get_or_create_posting(con, index_word, document_name)
    posting.frequency += 1
    posting.indexes.append(index)
    cur.execute("UPDATE Posting SET frequency = ?, indexes = ? WHERE word = ? AND documentName = ?",
                (posting.frequency, generate_indexes(posting.indexes), index_word, document_name))
    con.commit()


def get_all_document_postings(con, document_name):
    cur = con.cursor()
    cur.execute("SELECT * FROM Posting where documentName = ?", (document_name,))
    res = cur.fetchall()
    return list(map(lambda x: Posting(x[0], x[1], x[2], x[3]), res))


def get_all_word_postings(con, index_word):
    cur = con.cursor()
    cur.execute("SELECT * FROM Posting where word = ?", (index_word,))
    res = cur.fetchall()
    return list(map(lambda x: Posting(x[0], x[1], x[2], x[3]), res))


def get_all_multiword_postings_alt(con, index_words):
    cur = con.cursor()
    word_count = len(index_words)
    where_format = ("word = ? OR " * len(index_words))
    where_format = where_format[:len(where_format) - 4]
    index_words.append(word_count-1)
    query_args = tuple(index_words)
    # print(where_format)
    # print(words)

    cur.execute(f"SELECT documentName, SUM(frequency), GROUP_CONCAT(indexes, \";\") "
                f"FROM Posting "
                f"WHERE {where_format} "
                f"GROUP BY documentName "
                f"HAVING COUNT(*) > ?"
                f"ORDER BY SUM(frequency) DESC", query_args)
    res = cur.fetchall()
    return list(map(lambda x: SearchResult(x[0], x[1], x[2]), res))
    return res
    return list(map(lambda x: Posting(x[0], x[1], x[2], x[3]), res))


def add_index(con, index_word, document_name, index):
    insert_index_word(con, index_word)
    update_posting(con, index_word, document_name, index)


def generate_indexes(index_list):
    return ",".join(map(lambda x: str(x), sorted(list(set(index_list)))))


def parse_indexes(index_string):
    split = index_string.split(",")
    if len(split) == 0:
        return []
    return [int(x) for x in split if len(x) > 0]


if __name__ == '__main__':
    con = connection()

    cur = con.cursor()
    query = "varnost in zdravje".split(" ")
    for word in query:
        results = get_all_word_postings(con, word)


    # cur.execute("SELECT * FROM Posting")
    # res = cur.fetchall()
    # print(res)
    con.close()
