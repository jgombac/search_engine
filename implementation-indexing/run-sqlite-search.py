import database as db

if __name__ == '__main__':
    con = db.connection()
    results = db.get_all_multiword_postings(con, ["zdravje", 'varnost'])
    print(len(results))
    print("done")
