import database as db

if __name__ == '__main__':
    con = db.connection()
    results = db.get_all_multiword_postings_alt(con, ["zdravje", "varnost", "storitev"])
    print(len(results))
    print(results)
    print("done")
