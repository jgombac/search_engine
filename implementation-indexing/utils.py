import glob


def get_file(filename, encoding):
    with open(filename, 'r', encoding=encoding) as f:
        return f.read()


def save_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(data)


def get_page_filenames():
    return glob.glob("../pages/*/*.html")

