from utils import *
from preprocessing import preprocess, get_text
from database import add_index, connection


def build():
    con = connection()

    cur = con.cursor()
    cur.execute("DELETE FROM Posting")
    cur.execute("DELETE FROM IndexWord")
    con.commit()

    filenames = get_page_filenames()
    for filename in filenames:
        file = get_file(filename, "utf8")
        text = get_text(file)
        words = preprocess(text)

        for word in words:
            add_index(con, word[0], filename.replace("\\", "/").replace("../pages/", ""), word[1])

    con.close()

if __name__ == '__main__':
    build()